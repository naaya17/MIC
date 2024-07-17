#!/usr/bin/env python3
import json

DB_IMPL_STRUCTURE_JSON_PATH = "./data_structures/DBImpl.json"
with open(DB_IMPL_STRUCTURE_JSON_PATH) as f:
    DB_IMPL_STRUCTURE_JSON_PATH = json.load(f)

ARENA_STRUCTURE_JSON_PATH = "./data_structures/LevelDBArena.json"
with open(ARENA_STRUCTURE_JSON_PATH) as f:
    ARENA_STRUCTURE_JSON_PATH = json.load(f)
   
OPTIONS_STRUCTURE_JSON_PATH = "./data_structures/LevelDBOptions.json"
with open(OPTIONS_STRUCTURE_JSON_PATH) as f:
    OPTIONS_STRUCTURE_JSON_PATH = json.load(f)

SKIPLIST_STRUCTURE_JSON_PATH = "./data_structures/LevelDBSkipList.json"
with open(SKIPLIST_STRUCTURE_JSON_PATH) as f:
    SKIPLIST_STRUCTURE_JSON_PATH = json.load(f)

SKIPLIST_NODE_STRUCTURE_JSON_PATH = "./data_structures/LevelDBSkipListNode.json"
with open(SKIPLIST_NODE_STRUCTURE_JSON_PATH) as f:
    SKIPLIST_NODE_STRUCTURE_JSON_PATH = json.load(f)

VERSION_STRUCTURE_JSON_PATH = "./data_structures/LevelDBVersion.json"
with open(VERSION_STRUCTURE_JSON_PATH) as f:
    VERSION_STRUCTURE_JSON_PATH = json.load(f)

VERSION_SET_STRUCTURE_JSON_PATH = "./data_structures/LevelDBVersionSet.json"
with open(VERSION_SET_STRUCTURE_JSON_PATH) as f:
    VERSION_SET_STRUCTURE_JSON_PATH = json.load(f)

MEMTABLE_STRUCTURE_JSON_PATH = "./data_structures/MemTable.json"
with open(MEMTABLE_STRUCTURE_JSON_PATH) as f:
    MEMTABLE_STRUCTURE_JSON_PATH = json.load(f)

