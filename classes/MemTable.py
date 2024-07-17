#!/usr/bin/env python3

import errors

from interface import Object
from classes import logger
from classes.LevelDBSkipList import LevelDBSkipList
from classes import MEMTABLE_STRUCTURE_JSON_PATH

class MemTable(Object):
    """MemTable object."""
    def __init__(self, mem_handle, addr):
        super().__init__(mem_handle, addr)
        self._base_addr = addr

        for key, value in MEMTABLE_STRUCTURE_JSON_PATH.items():
            setattr(self, key, value)

        self._buf = self._mem_handle.get_reader().read(self._base_addr, int(self.struct_size, 16))

    def validate(self):
        try:
            table = LevelDBSkipList(self._mem_handle, addr=self._base_addr + int(self.table_['offset'], 16))
            assert table.validate()

        except Exception as exception:
            logger.debug('{0}: {1}'.format(errors.MemTableValidationException, exception))
            raise errors.MemTableValidationException
        
        return True

    def set_values(self):
        
        table = LevelDBSkipList(self._mem_handle, addr=self._base_addr + int(self.table_['offset'], 16))
        table.set_values()
        setattr(self, 'table_', str(table)) 
