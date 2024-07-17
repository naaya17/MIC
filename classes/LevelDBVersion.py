#!/usr/bin/env python3

import errors
import extractor
import validator


from interface import Object
from classes import logger
from classes import VERSION_STRUCTURE_JSON_PATH

class LevelDBVersion(Object):
    """LevelDBVersion object."""
    def __init__(self, mem_handle, addr):
        super().__init__(mem_handle, addr)
        self._base_addr = addr

        for key, value in VERSION_STRUCTURE_JSON_PATH.items():
            setattr(self, key, value)

        self._buf = self._mem_handle.get_reader().read(self._base_addr, int(self.struct_size, 16))

    def validate(self):
        try:
            assert validator.validate_pointer(self._buf, self.vset_, 64, self._mem_handle)
            assert validator.validate_pointer(self._buf, self.next_, 64, self._mem_handle)
            assert validator.validate_pointer(self._buf, self.prev_, 64, self._mem_handle)
            assert validator.validate_interger(self._buf, self.file_to_compact_level_, num_bits=32)

            
        except Exception as exception:
            logger.debug('{0}: {1}'.format(errors.LevelDBVersionValidationException, exception))
            raise errors.LevelDBVersionValidationException
        
        return True 

    def set_values(self):
        self.vset_['value'] = extractor.to_pointer(self._buf, self.vset_)
        self.next_['value'] = extractor.to_pointer(self._buf, self.next_)
        self.prev_['value'] = extractor.to_pointer(self._buf, self.prev_)
        self.file_to_compact_level_['value'] = extractor.to_interger(self._buf, self.file_to_compact_level_, num_bits=32)
