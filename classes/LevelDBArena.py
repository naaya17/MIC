#!/usr/bin/env python3

import io
import errors
import struct

import extractor
import validator
import classifier
import deserializer as ds
import indexeddb_util

from interface import Object
from indexeddb_util import Record
from indexeddb_util import KeyState
from classes import logger
from classes import ARENA_STRUCTURE_JSON_PATH

class LevelDBArena(Object):
    """LevelDBArena object."""
    
    def __init__(self, mem_handle, addr, max_height):
        super().__init__(mem_handle, addr)
        self._base_addr = addr
        self._block_size = 4096
        self._max_height = max_height

        for key, value in ARENA_STRUCTURE_JSON_PATH.items():
            setattr(self, key, value)

        self._buf = self._mem_handle.get_reader().read(self._base_addr, int(self.struct_size, 16))

    def validate(self):
        try:
            assert validator.validate_vector(self._buf, self.blocks_, self._mem_handle, 64, False, 'little')
            
        except Exception as exception:
            logger.debug('{0}: {1}'.format(errors.LevelDBArenaValidationException, exception))
            raise errors.LevelDBArenaValidationException
        
        return True 

    def set_values(self):
        block_entries = extractor.to_vector(self._buf, self.blocks_, self._mem_handle, 64, 'little')
        self.blocks_['value'] = block_entries
        raw_records = self._get_block_data(block_entries)
        data, global_metadata, database_metadata, object_store_meta = ds.get_data(raw_records)
        classifier.classify_records(data, raw_records, global_metadata, database_metadata, object_store_meta)

    def _get_block_data(self, block_entries):
        raw_records = set()
        buf = self._mem_handle.get_reader().read(block_entries[0], self._block_size)
        for i in range(8, self._max_height * 8, 8):
            ptr = struct.unpack("<Q", buf[i:i+8])[0]
            if ptr == 0:
                continue
            
            raw_records.add(struct.unpack("<Q", self._mem_handle.get_reader().read(ptr, 8))[0])
            while self._is_valid_range(block_entries, ptr):
                raw_records.add(struct.unpack("<Q", self._mem_handle.get_reader().read(ptr, 8))[0])
                ptr = struct.unpack("<Q", self._mem_handle.get_reader().read(ptr + i, 8))[0]
            
        records = list()
        
        for offset in raw_records:
            record = self._get_raw_records(offset, block_entries)
            if record is not None:
                records.append(record)
        return records
        
    def _is_valid_range(self, block_entries, ptr):
        for i in range(0, len(block_entries)):
            if block_entries[i] <= ptr and block_entries[i] + self._block_size >= ptr:
                return True
        return False
    
    def _get_raw_records(self, key_offset, block_entries):
        for i in range(0, len(block_entries)):
            if block_entries[i] <= key_offset and block_entries[i] + self._block_size >= key_offset:
                try:
                    buf = io.BytesIO(self._mem_handle.get_reader().read(block_entries[i], self._block_size))
                except Exception as exception:
                    print(exception)
                    continue
                buf.seek(key_offset - block_entries[i])
                key_length = indexeddb_util.read_le_varint(buf, is_google_32bit=True)
                key = buf.read(key_length)
                seq =  (struct.unpack("<Q", key[-8:])[0]) >> 8
                type = KeyState.Deleted if key[-8] == 0 else KeyState.Live
                if key_length > 8:
                    key = key[0:-8]
                value_length = indexeddb_util.read_le_varint(buf, is_google_32bit=True) 
                value = buf.read(value_length)

                return Record.record(key, value, seq, key_offset, type)
    
    


