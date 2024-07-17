#!/usr/bin/env python3

import errors
import extractor
import validator


from interface import Object
from classes import logger
from classes.MemTable import MemTable
from classes.LevelDBOptions import LevelDBOptions
from classes.LevelDBVersionSet import LevelDBVersionSet
from classes import DB_IMPL_STRUCTURE_JSON_PATH

class DBImpl(Object):
    """DBImpl object."""
    def __init__(self, mem_handle, buff, addr):
        super().__init__(mem_handle, addr)
        self._base_addr = addr

        for key, value in DB_IMPL_STRUCTURE_JSON_PATH.items():
            setattr(self, key, value)
        
        self._buf = buff

    def validate(self):
        try:
            assert validator.validate_boolean(self._buf, self.owns_info_log_)
            assert validator.validate_boolean(self._buf, self.shutting_down_)
            assert validator.validate_boolean(self._buf, self.owns_cache_)
            assert validator.validate_pointer(self._buf, self.table_cache_, 64, self._mem_handle)
            assert validator.validate_pointer(self._buf, self.db_lock_, 64, self._mem_handle)

            assert validator.validate_string(self._buf, self.dbname_, base_addr = self._base_addr, mem_handle= self._mem_handle, is_nullable=True)
            assert validator.validate_pointer(self._buf, self.mem_, 64, self._mem_handle)
            assert validator.validate_boolean(self._buf, self.has_imm_)
            if extractor.to_boolean(self._buf, self.has_imm_):
                assert validator.validate_pointer(self._buf, self.imm_)
            assert validator.validate_interger(self._buf, self.logfile_number_)
            assert validator.validate_pointer(self._buf, self.versions_, 64, self._mem_handle)

            ldboption = LevelDBOptions(self._mem_handle, addr=self._base_addr + int(self.options_['offset'], 16))
            assert ldboption.validate()

            version_set_ptr = self._buf[int(self.versions_['offset'], 16) : int(self.versions_['offset'], 16) + 8]
            version_set_ptr = int.from_bytes(version_set_ptr, byteorder='little')
            version_set = LevelDBVersionSet(self._mem_handle, addr=version_set_ptr)
            assert version_set.validate()

            mem_ptr = self._buf[int(self.mem_['offset'], 16) : int(self.mem_['offset'], 16) + 8]
            mem_ptr = int.from_bytes(mem_ptr, byteorder='little')
            mem = MemTable(self._mem_handle, addr=mem_ptr)
            assert mem.validate()
           
            if extractor.to_boolean(self._buf, self.has_imm_):
                imm_ptr = self._buf[int(self.imm_['offset'], 16) : int(self.imm_['offset'], 16) + 8]
                imm_ptr = int.from_bytes(imm_ptr, byteorder='little')
                imm = MemTable(self._mem_handle, addr=imm_ptr)
                assert imm.validate()
            
        except Exception as exception:
            # logger.debug('{0}: {1}'.format(errors.DBImplValidationException, exception))
            raise errors.DBImplValidationException
        
        return True 

    def set_values(self):
        
        ldboption = LevelDBOptions(self._mem_handle, addr=self._base_addr + int(self.options_['offset'], 16))
        ldboption.set_values()
        setattr(self, 'options_', str(ldboption))
        
        self.dbname_['value'] = extractor.to_string(self._buf, self.dbname_, base_addr = self._base_addr, mem_handle= self._mem_handle, is_nullable=True)
        self.dbname_['value'] = self.dbname_['value'].replace('\\', '\\\\')
        self.has_imm_['value'] = extractor.to_boolean(self._buf, self.has_imm_)
        self.logfile_number_['value'] = extractor.to_interger(self._buf, self.logfile_number_)

        mem_ptr = self._buf[int(self.mem_['offset'], 16) : int(self.mem_['offset'], 16) + 8]
        mem_ptr = int.from_bytes(mem_ptr, byteorder='little')
        mem = MemTable(self._mem_handle, addr=mem_ptr)
        mem.set_values()
        setattr(self, 'mem_', str(mem))
        
        if extractor.to_boolean(self._buf, self.has_imm_):
            imm_ptr = self._buf[int(self.imm_['offset'], 16) : int(self.imm_['offset'], 16) + 8]
            imm_ptr = int.from_bytes(imm_ptr, byteorder='little')
            imm = MemTable(self._mem_handle, addr=imm_ptr)
            imm.set_values()
            setattr(self, 'imm_', str(imm))
        
        version_set_ptr = self._buf[int(self.versions_['offset'], 16) : int(self.versions_['offset'], 16) + 8]
        version_set_ptr = int.from_bytes(version_set_ptr, byteorder='little')
        version_set = LevelDBVersionSet(self._mem_handle, addr=version_set_ptr)
        version_set.set_values()
        setattr(self, 'versions_', str(version_set))
