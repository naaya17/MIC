#!/usr/bin/env python3

import errors
import extractor
import validator


from interface import Object
from classes import logger
from classes.LevelDBArena import LevelDBArena
from classes.LevelDBSkipListNode import LevelDBSkipListNode
from classes import SKIPLIST_STRUCTURE_JSON_PATH

class LevelDBSkipList(Object):
    """LevelDBSkipList object."""
    
    def __init__(self, mem_handle, addr):
        super().__init__(mem_handle, addr)
        self._base_addr = addr

        for key, value in SKIPLIST_STRUCTURE_JSON_PATH.items():
            setattr(self, key, value)

        self._buf = self._mem_handle.get_reader().read(self._base_addr, int(self.struct_size, 16))

    def validate(self):
        try:
            assert validator.validate_interger(self._buf, self.max_height_, num_bits=32)
            _max_height = extractor.to_interger(self._buf, self.max_height_, num_bits=32)
            assert _max_height > 0 and _max_height <= 12

            arena_ptr = self._mem_handle.get_reader().read(self._base_addr + int(self.arena_['offset'], 16), 8)
            arena_ptr = int.from_bytes(arena_ptr, byteorder='little')
            arena = LevelDBArena(self._mem_handle, addr=arena_ptr, max_height=_max_height)
            assert arena.validate()

            assert validator.validate_pointer(self._buf, self.head_, 64, self._mem_handle)

            head_ptr = self._mem_handle.get_reader().read(self._base_addr + int(self.head_['offset'], 16), 8)
            head_ptr = int.from_bytes(head_ptr, byteorder='little')
            head = LevelDBSkipListNode(self._mem_handle, addr=head_ptr)
            assert head.validate()
            
        except Exception as exception:
            logger.debug('{0}: {1}'.format(errors.LevelDBSkipListValidationException, exception))
            raise errors.LevelDBSkipListValidationException
        
        return True 

    def set_values(self):
        
        _max_height = extractor.to_interger(self._buf, self.max_height_, num_bits=32)
        self.max_height_['value'] = _max_height
        arena_ptr = self._mem_handle.get_reader().read(self._base_addr + int(self.arena_['offset'], 16), 8)
        arena_ptr = int.from_bytes(arena_ptr, byteorder='little')
        arena = LevelDBArena(self._mem_handle, addr=arena_ptr, max_height=_max_height)
        arena.set_values()
        setattr(self, 'arena_', str(arena))
        
        self.head_['value'] = extractor.to_pointer(self._buf, self.head_)

        head_ptr = self._mem_handle.get_reader().read(self._base_addr + int(self.head_['offset'], 16), 8)
        head_ptr = int.from_bytes(head_ptr, byteorder='little')
        head = LevelDBSkipListNode(self._mem_handle, addr=head_ptr)
        head.set_values()
        setattr(self, 'head_', str(head))