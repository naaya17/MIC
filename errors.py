#!/usr/bin/env python3

class NullException(Exception):
    pass

class VectorValueError(Exception):
    pass

class InvalidRangeException(Exception):
    pass 

class LevelDBArenaValidationException(Exception):
    pass

class LevelDBSkipListValidationException(Exception):
    pass

class LevelDBSkipListNodeValidationException(Exception):
    pass

class MemTableValidationException(Exception):
    pass

class LevelDBVersionValidationException(Exception):
    pass

class LevelDBVersionSetValidationException(Exception):
    pass

class DBImplValidationException(Exception):
    pass

class LevelDBOptionsValidationException(Exception):
    pass

class UnknownTypeException(Exception):
    pass