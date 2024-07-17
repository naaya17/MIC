#!/usr/bin/env python3
import io
import enum
import types
import struct
import typing
import datetime
import dataclasses


class KeyState(enum.Enum):
    Deleted = 0
    Live = 1
    Unknown = 2

@dataclasses.dataclass(frozen=True)
class Record:
   key: bytes
   value: bytes
   seq: int
   offset: int
   type: KeyState

   @classmethod
   def record(cls, key: bytes, value: bytes, seq: int, offset: int, type: KeyState):
      return cls(key, value, seq, offset, type)

@dataclasses.dataclass(frozen=True)
class DatabaseId:
    dbid_no: int
    origin: str
    name: str

class GlobalMetadata:
    def __init__(self, raw_meta_dict: dict):
        # TODO: more of these meta types if required
        self.backing_store_schema_version = None
        if raw_schema_version := raw_meta_dict.get("\x00\x00\x00\x00\x00"):
            self.backing_store_schema_version = le_varint_from_bytes(raw_schema_version)

        self.max_allocated_db_id = None
        if raw_max_db_id := raw_meta_dict.get("\x00\x00\x00\x00\x01"):
            self.max_allocated_db_id = le_varint_from_bytes(raw_max_db_id)

        database_ids_raw = (raw_meta_dict[x] for x in raw_meta_dict
                            if x.startswith(b"\x00\x00\x00\x00\xc9"))

        dbids = []
        for dbid_rec in database_ids_raw:
            with io.BytesIO(dbid_rec.key[5:]) as buff:
                origin_length = read_le_varint(buff)
                origin = buff.read(origin_length * 2).decode("utf-16-be")
                db_name_length = read_le_varint(buff)
                db_name = buff.read(db_name_length * 2).decode("utf-16-be")

            db_id_no = le_varint_from_bytes(dbid_rec.value)

            dbids.append(DatabaseId(db_id_no, origin, db_name))

        self.db_ids = tuple(dbids)

class DatabaseMetadataType(enum.IntEnum):
    OriginName = 0  # String
    DatabaseName = 1  # String
    IdbVersionString = 2  # String (and obsolete)
    MaximumObjectStoreId = 3  # Int
    IdbVersion = 4  # Varint
    BlobNumberGeneratorCurrentNumber = 5  # Varint


class DatabaseMetadata:
    def __init__(self, raw_meta: dict):
        self._metas = types.MappingProxyType(raw_meta)

    def get_meta(self, db_id: int, meta_type: DatabaseMetadataType) -> typing.Optional[typing.Union[str, int]]:
        record = self._metas.get((db_id, meta_type))
        if not record:
            return None

        if meta_type == DatabaseMetadataType.MaximumObjectStoreId:
            return le_varint_from_bytes(record.value)

        # TODO
        raise NotImplementedError()
    
class ObjectStoreMetadataType(enum.IntEnum):
    StoreName = 0  # String
    KeyPath = 1  # IDBKeyPath
    AutoIncrementFlag = 2  # Bool
    IsEvictable = 3  # Bool (and obsolete apparently)
    LastVersionNumber = 4  # Int
    MaximumAllocatedIndexId = 5  # Int
    HasKeyPathFlag = 6  # Bool (and obsolete apparently)
    KeygeneratorCurrentNumber = 7  # Int


class ObjectStoreMetadata:
    # All metadata fields are prefaced by a 0x00 byte
    def __init__(self, raw_meta: dict):
        self._metas = types.MappingProxyType(raw_meta)

    def get_meta(self, db_id: int, obj_store_id: int, meta_type: ObjectStoreMetadataType):
        record = self._metas.get((db_id, obj_store_id, meta_type))
        if not record:
            return None

        if meta_type == ObjectStoreMetadataType.StoreName:
            return record.value.decode("utf-16-be")

        # TODO
        raise NotImplementedError()


        
class IdbKeyType(enum.IntEnum):
    Null = 0
    String = 1
    Date = 2
    Number = 3
    Array = 4
    MinKey = 5
    Binary = 6


class IdbKey:
    # See: https://github.com/chromium/chromium/blob/master/content/browser/indexed_db/indexed_db_leveldb_coding.cc
    def __init__(self, buffer: bytes):
        self.raw_key = buffer
        self.key_type = IdbKeyType(buffer[0])
        raw_key = buffer[1:]

        if self.key_type == IdbKeyType.Null:
            self.value = None
            self._raw_length = 1
        elif self.key_type == IdbKeyType.String:
            str_len, varint_raw = _le_varint_from_bytes(raw_key)
            self.value = raw_key[len(varint_raw):len(varint_raw) + str_len * 2].decode("utf-16-be")
            self._raw_length = 1 + len(varint_raw) + str_len * 2
        elif self.key_type == IdbKeyType.Date:
            ts, = struct.unpack("<d", raw_key[0:8])
            self.value = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=ts)
            self._raw_length = 9
        elif self.key_type == IdbKeyType.Number:
            self.value = struct.unpack("<d", raw_key[0:8])[0]
            self._raw_length = 9
        elif self.key_type == IdbKeyType.Array:
            array_count, varint_raw = _le_varint_from_bytes(raw_key)
            raw_key = raw_key[len(varint_raw):]
            self.value = []
            self._raw_length = 1 + len(varint_raw)
            for i in range(array_count):
                key = IdbKey(raw_key)
                raw_key = raw_key[key._raw_length:]
                self._raw_length += key._raw_length
                self.value.append(key)
            self.value = tuple(self.value)
        elif self.key_type == IdbKeyType.MinKey:
            # TODO: not sure what this actually implies, the code doesn't store a value
            self.value = None
            self._raw_length = 1
            raise NotImplementedError()
        elif self.key_type == IdbKeyType.Binary:
            bin_len, varint_raw = _le_varint_from_bytes(raw_key)
            self.value = raw_key[len(varint_raw):len(varint_raw) + bin_len]
            self._raw_length = 1 + len(varint_raw) + bin_len
        else:
            raise ValueError()  # Shouldn't happen

        # trim the raw_key in case this is an inner key:
        self.raw_key = self.raw_key[0: self._raw_length]

    def __repr__(self):
        return f"<IdbKey {self.value}>"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if not isinstance(other, IdbKey):
            raise NotImplementedError()
        return self.raw_key == other.raw_key

    def __ne__(self, other):
        return not self == other
    


def _read_le_varint(stream: typing.BinaryIO, *, is_google_32bit=False) -> typing.Optional[typing.Tuple[int, bytes]]:
    """Read varint from a stream.
    If the read is successful: returns a tuple of the (unsigned) value and the raw bytes making up that varint,
    otherwise returns None.
    Can be switched to limit the varint to 32 bit."""
    i = 0
    result = 0
    underlying_bytes = []
    limit = 5 if is_google_32bit else 10
    while i < limit:
        raw = stream.read(1)
        if len(raw) < 1:
            return None
        tmp, = raw
        underlying_bytes.append(tmp)
        result |= ((tmp & 0x7f) << (i * 7))
        if (tmp & 0x80) == 0:
            break
        i += 1
    return result, bytes(underlying_bytes)

def read_le_varint(stream: typing.BinaryIO, *, is_google_32bit=False) -> typing.Optional[int]:
    """Convenience version of _read_le_varint that only returns the value or None"""
    x = _read_le_varint(stream, is_google_32bit=is_google_32bit)
    if x is None:
        return None
    else:
        return x[0]

def le_varint_from_bytes(data: bytes) -> typing.Optional[int]:
    with io.BytesIO(data) as buff:
        return read_le_varint(buff)
    
def _le_varint_from_bytes(data: bytes) -> typing.Optional[tuple[int, bytes]]:
    with io.BytesIO(data) as buff:
        return _read_le_varint(buff)
    
@staticmethod
def read_prefix(stream: typing.BinaryIO) -> tuple[int, int, int, int]:
    """
    :param stream: file-like to read the prefix from
    :return: a tuple of db_id, object_store_id, index_id, length of the prefix
    """
    lengths_bytes = stream.read(1)
    if not lengths_bytes:
        raise ValueError("Couldn't get enough data when reading prefix length")
    lengths = lengths_bytes[0]
    db_id_size = ((lengths >> 5) & 0x07) + 1
    object_store_size = ((lengths >> 2) & 0x07) + 1
    index_size = (lengths & 0x03) + 1

    db_id_raw = stream.read(db_id_size)
    object_store_raw = stream.read(object_store_size)
    index_raw = stream.read(index_size)

    if (len(db_id_raw) != db_id_size or
            len(object_store_raw) != object_store_size or
            len(index_raw) != index_size):
        raise ValueError("Couldn't read enough bytes for the prefix")

    db_id = int.from_bytes(db_id_raw, "little")
    object_store_id = int.from_bytes(object_store_raw, "little")
    index_id = int.from_bytes(index_raw, "little")

    return db_id, object_store_id, index_id, (db_id_size + object_store_size + index_size + 1)