#!/usr/bin/env python3

import errors
import extractor
import validator


from interface import Object
from classes import logger
from classes import SKIPLIST_NODE_STRUCTURE_JSON_PATH

class LevelDBSkipListNode(Object):
    """LevelDBSkipListNode object."""
    def __init__(self, mem_handle, addr):
        super().__init__(mem_handle, addr)
        self._base_addr = addr

        for key, value in SKIPLIST_NODE_STRUCTURE_JSON_PATH.items():
            setattr(self, key, value)

        self._buf = self._mem_handle.get_reader().read(self._base_addr, int(self.struct_size, 16))

    def validate(self):
        try:
            assert validator.validate_pointer(self._buf, self.key_, 64, self._mem_handle, 'little', True)
            assert validator.validate_pointer(self._buf, self.next_, 64, self._mem_handle, 'little', True)
            
        except Exception as exception:
            logger.debug('{0}: {1}'.format(errors.LevelDBSkipListNodeValidationException, exception))
            raise errors.LevelDBSkipListNodeValidationException
        
        return True 

    def set_values(self):
        self.key_['value'] = extractor.to_pointer(self._buf, self.key_)
        self.next_['value'] = extractor.to_pointer(self._buf, self.next_)


