#!/usr/bin/env python3

import errors
import extractor
import validator


from interface import Object
from classes import logger
from classes import OPTIONS_STRUCTURE_JSON_PATH

class LevelDBOptions(Object):
    """LevelDBOptions object."""
    def __init__(self, mem_handle, addr):
        super().__init__(mem_handle, addr)
        self._base_addr = addr

        for key, value in OPTIONS_STRUCTURE_JSON_PATH.items():
            setattr(self, key, value)

        self._buf = self._mem_handle.get_reader().read(self._base_addr, int(self.struct_size, 16))

    def validate(self):
        try:
            assert validator.validate_boolean(self._buf, self.create_if_missing)
            assert validator.validate_boolean(self._buf, self.error_if_exists)
            assert validator.validate_interger(self._buf, self.write_buffer_size)
            assert validator.validate_interger(self._buf, self.block_size)
            assert validator.validate_interger(self._buf, self.max_file_size)
            assert validator.validate_enum(self._buf, self.compression, num_bits=32)
            
        except Exception as exception:
            logger.debug('{0}: {1}'.format(errors.LevelDBOptionsValidationException, exception))
            raise errors.LevelDBOptionsValidationException
        
        return True 

    def set_values(self):
        
        self.create_if_missing['value'] = extractor.to_boolean(self._buf, self.create_if_missing)
        self.error_if_exists['value'] = extractor.to_boolean(self._buf, self.error_if_exists)
        self.write_buffer_size['value'] = extractor.to_interger(self._buf, self.write_buffer_size)
        self.block_size['value'] = extractor.to_interger(self._buf, self.block_size)
        self.max_file_size['value'] = extractor.to_interger(self._buf, self.max_file_size)
        self.compression['value'] = extractor.to_enum(self._buf, self.compression, num_bits=32)

