#!/usr/bin/env python3
import io
import struct
import typing
import dataclasses

import indexeddb_util
import ccl_blink_value_deserializer
import ccl_v8_value_deserializer

from indexeddb_util import KeyState

def get_data(records):
        global_metadata_raw = {}
        database_metadata_raw = {}
        objectstore_metadata_raw = {}
        data = []

        for record in records:
            if record.key.startswith(b"\x00\x00\x00\x00") and record.type == KeyState.Live:
                if record.key not in global_metadata_raw or global_metadata_raw[record.key].seq < record.seq:
                    global_metadata_raw[record.key] = record
            
            
            if record.key[3] == 1:
                try:
                    db_id, object_store, index_id, length = indexeddb_util.read_prefix(io.BytesIO(record.key))
                    key = indexeddb_util.IdbKey(record.key[length:])
                    if not record.value:
                        continue
                    value_version, varint_raw = indexeddb_util._le_varint_from_bytes(record.value)
                    val_idx = len(varint_raw)
                    # read the blink envelope
                    precursor = read_record_precursor(
                    key, 0, 0, record.value[val_idx:], bad_deserializer_data_handler=None)
                    if precursor is None:
                        continue  # only returns None on error, handled in the function if bad_deserializer_data_handler can

                    blink_version, obj_raw, trailer, external_path = precursor

                    try:
                        deserializer = ccl_v8_value_deserializer.Deserializer(
                            obj_raw, host_object_delegate=None)
                        value = deserializer.read()
                        data.append((db_id, object_store, record.seq, record.type, key.value, value))
                        
                    except Exception as exception:
                        continue
                except Exception:
                    continue

        global_metadata = indexeddb_util.GlobalMetadata(global_metadata_raw)
        
        for db_id in global_metadata.db_ids:
            if db_id.dbid_no > 0x7f:
                raise NotImplementedError("there could be this many dbs, but I don't support it yet")

            prefix_database = bytes([0, db_id.dbid_no, 0, 0])
            prefix_objectstore = bytes([0, db_id.dbid_no, 0, 0, 50])

            for record in reversed(records):
                if record.key.startswith(prefix_database) and record.type == KeyState.Live:
                    meta_type = record.key[len(prefix_database)]
                    old_version = database_metadata_raw.get((db_id.dbid_no, meta_type))
                    if old_version is None or old_version.seq < record.seq:
                        database_metadata_raw[(db_id.dbid_no, meta_type)] = record
                if record.key.startswith(prefix_objectstore) and record.type == KeyState.Live:
                    try:
                        objstore_id, varint_raw = indexeddb_util._le_varint_from_bytes(record.key[len(prefix_objectstore):])
                    except TypeError:
                        continue

                    meta_type = record.key[len(prefix_objectstore) + len(varint_raw)]
                    old_version = objectstore_metadata_raw.get((db_id.dbid_no, objstore_id, meta_type))
                    if old_version is None or old_version.seq < record.seq:
                        objectstore_metadata_raw[(db_id.dbid_no, objstore_id, meta_type)] = record

        return data, global_metadata, indexeddb_util.DatabaseMetadata(database_metadata_raw), indexeddb_util.ObjectStoreMetadata(objectstore_metadata_raw)


def read_record_precursor(key, db_id: int, store_id: int, buffer: bytes, # type: ignore
        bad_deserializer_data_handler: None, # type: ignore
        external_data_path: typing.Optional[str] = None):
    val_idx = 0
    trailer = None
    blink_type_tag = buffer[val_idx]
    if blink_type_tag != 0xff:
        # TODO: probably don't want to fail hard here long term...
        if bad_deserializer_data_handler is not None:
            bad_deserializer_data_handler(key, buffer)
            return None
        else:
            raise ValueError("Blink type tag not present")

    val_idx += 1

    blink_version, varint_raw = indexeddb_util._le_varint_from_bytes(buffer[val_idx:])

    val_idx += len(varint_raw)

    # Peek the next byte to work out if the data is held externally:
    # third_party/blink/renderer/modules/indexeddb/idb_value_wrapping.cc
    if blink_version >= BlinkTrailer.MIN_WIRE_FORMAT_VERSION_FOR_TRAILER:
        trailer = BlinkTrailer.from_buffer(buffer, val_idx)  # TODO: do something with the trailer
        val_idx += BlinkTrailer.TRAILER_SIZE

    obj_raw = io.BytesIO(buffer[val_idx:])

    return blink_version, obj_raw, trailer, external_data_path

@dataclasses.dataclass(frozen=True)
class BlinkTrailer:
    # third_party/blink/renderer/bindings/core/v8/serialization/trailer_reader.h
    offset: int
    length: int

    TRAILER_SIZE: typing.ClassVar[int] = 13
    MIN_WIRE_FORMAT_VERSION_FOR_TRAILER: typing.ClassVar[int] = 21

    @classmethod
    def from_buffer(cls, buffer, trailer_offset: int):
        tag, offset, length = struct.unpack(">cQI", buffer[trailer_offset: trailer_offset + BlinkTrailer.TRAILER_SIZE])
        if tag != ccl_blink_value_deserializer.Constants.tag_kTrailerOffsetTag:
            raise ValueError(
                f"Trailer doesn't start with kTrailerOffsetTag "
                f"(expected: 0x{ccl_blink_value_deserializer.Constants.tag_kTrailerOffsetTag.hex()}; "
                f"got: 0x{tag.hex()}")

        return BlinkTrailer(offset, length)

