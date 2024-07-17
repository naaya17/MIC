#!/usr/bin/env python3

import errors
import extractor
import validator


from interface import Object
from classes import logger
from classes.LevelDBVersion import LevelDBVersion
from classes import VERSION_SET_STRUCTURE_JSON_PATH

class LevelDBVersionSet(Object):
    """LevelDBVersionSet object."""
    def __init__(self, mem_handle, addr):
        super().__init__(mem_handle, addr)
        self._base_addr = addr

        for key, value in VERSION_SET_STRUCTURE_JSON_PATH.items():
            setattr(self, key, value)

        self._buf = self._mem_handle.get_reader().read(self._base_addr, int(self.struct_size, 16))

    def validate(self):
        try:
            assert validator.validate_string(self._buf, self.dbname_, base_addr = self._base_addr, mem_handle= self._mem_handle, is_nullable=True)
            assert validator.validate_interger(self._buf, self.next_file_number_)
            assert validator.validate_interger(self._buf, self.manifest_file_number_)
            assert validator.validate_interger(self._buf, self.last_sequence_)
            assert validator.validate_interger(self._buf, self.log_number_)
            assert validator.validate_interger(self._buf, self.prev_log_number_)
            assert validator.validate_pointer(self._buf, self.current_, 64, self._mem_handle)

            version_ptr = self._mem_handle.get_reader().read(self._base_addr + int(self.current_['offset'], 16), 8)
            version_ptr = int.from_bytes(version_ptr, byteorder='little')
            version = LevelDBVersion(self._mem_handle, addr=version_ptr)
            assert version.validate()
            
        except Exception as exception:
            logger.debug('{0}: {1}'.format(errors.LevelDBVersionSetValidationException, exception))
            raise errors.LevelDBVersionSetValidationException
        
        return True 

    def set_values(self):
        
        self.dbname_['value'] = extractor.to_string(self._buf, self.dbname_, base_addr = self._base_addr, mem_handle= self._mem_handle, is_nullable=True)
        self.dbname_['value'] = self.dbname_['value'].replace('\\', '\\\\')
        self.next_file_number_['value'] = extractor.to_interger(self._buf, self.next_file_number_)
        self.manifest_file_number_['value'] = extractor.to_interger(self._buf, self.manifest_file_number_)
        self.last_sequence_['value'] = extractor.to_interger(self._buf, self.last_sequence_)
        self.log_number_['value'] = extractor.to_interger(self._buf, self.log_number_)
        self.prev_log_number_['value'] = extractor.to_interger(self._buf, self.prev_log_number_)
        self.current_['value'] = extractor.to_pointer(self._buf, self.current_)

        version_ptr = self._mem_handle.get_reader().read(self._base_addr + int(self.current_['offset'], 16), 8)
        version_ptr = int.from_bytes(version_ptr, byteorder='little')
        version = LevelDBVersion(self._mem_handle, addr=version_ptr)
        version.set_values()
        setattr(self, 'current_', str(version))