#!/usr/bin/env python3

import enum
import logger
import sqlite3


class TABLE_TYPE(enum.Enum):
    Metadata = 0
    Data = 1
    Unclassified = 2

class DATA_TYPE(enum.Enum):
    Metadata = 0
    IndexedDBData = 1
    LevelDBData = 2

def check_table_exists(db_path, table_name):
    conn = sqlite3.connect('results/'+db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    
    table_exists = cursor.fetchone() is not None

    cursor.close()
    conn.close()
    
    return table_exists

def create_table(database_name, table_name, type:TABLE_TYPE):
    try:
        conn = sqlite3.connect('results/'+database_name)
        cursor = conn.cursor()

        if type == TABLE_TYPE.Metadata:
            cursor.execute('''CREATE TABLE IF NOT EXISTS Metadata (
                                id INTEGER PRIMARY KEY,
                                database_id INTEGER NOT NULL,
                                database TEXT NOT NULL,
                                object_store_id INTEGER NOT NULL,
                                object_store TEXT NOT NULL
                            )''')
        elif type == TABLE_TYPE.Data:
            cursor.execute('''CREATE TABLE IF NOT EXISTS '''+table_name+''' (
                                id INTEGER PRIMARY KEY,
                                database_id INTEGER NOT NULL,
                                database TEXT NOT NULL,
                                object_store_id INTEGER NOT NULL,
                                object_store TEXT NOT NULL,
                                sequence_number INTEGER NOT NULL,
                                key_state TEXT NOT NULL,
                                key TEXT NOT NULL,
                                value  TEXT NOT NULL
                            )''')
        elif type == TABLE_TYPE.Unclassified:
            cursor.execute('''CREATE TABLE IF NOT EXISTS Unclassified (
                                id INTEGER PRIMARY KEY,
                                database_id INTEGER,
                                object_store_id INTEGER,
                                sequence_number INTEGER NOT NULL,
                                key_state TEXT NOT NULL,
                                key TEXT NOT NULL,
                                value  TEXT NOT NULL
                            )''')

        conn.commit()
        conn.close()
    except Exception as exception:
        logger.debug('{0}: {1}'.format('Exporter', exception))

def insert_records(database_name, records, type:DATA_TYPE):
    try:
        if type == DATA_TYPE.Metadata:
            conn = sqlite3.connect('results/'+database_name)
            cursor = conn.cursor()
            cursor.executemany("INSERT INTO Metadata (database_id, database, object_store_id, object_store) VALUES (?, ?, ?, ?)", records)
            conn.commit()
            conn.close()
        elif type == DATA_TYPE.IndexedDBData:
            conn = sqlite3.connect('results/'+database_name)
            cursor = conn.cursor()

            cursor.execute('SELECT database_id, object_store_id, database, object_store FROM Metadata')
            metadata_records = cursor.fetchall()
            metadata_dict = {(row[0], row[1]): (row[2], row[3]) for row in metadata_records}
            
            for record in records:
                try:
                    database_id = record[0]
                    object_store_id = record[1]

                    if (database_id, object_store_id) in metadata_dict:
                        table_name, object_store_name = metadata_dict[(database_id, object_store_id)]
                        table_name = table_name.replace(':', '_').replace('-', '_').replace(' ', '_')
                        cursor.execute(f'''INSERT INTO {table_name} (database_id, database, object_store_id, object_store, sequence_number, key_state, key, value) 
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                                    (record[0], table_name, record[1], object_store_name, 
                                        record[2], record[3].name, str(record[4]), str(record[5])))
                    else:
                        cursor.execute('''INSERT INTO Unclassified (database_id, object_store_id, sequence_number, key_state, key, value) 
                                        VALUES (?, ?, ?, ?, ?, ?)''', 
                                    (record[0], record[1], record[2], record[3].name, str(record[4]), str(record[5])))

                except Exception as exception:
                    logger.debug('{0}: {1}'.format('SQLite', exception))
                    continue
            conn.commit()
            conn.close()
        elif type == DATA_TYPE.LevelDBData:
            conn = sqlite3.connect('results/'+database_name)
            cursor = conn.cursor()
            for record in records:
                try:
                    cursor.execute('''INSERT INTO Unclassified (database_id, object_store_id, sequence_number, key_state, key, value) 
                                    VALUES (?, ?, ?, ?, ?, ?)''', 
                                    ('', '', record.seq, record.type.name, record.key.decode('iso-8859-1', 'replace'), record.value.decode('iso-8859-1', 'replace')))
                
                except Exception as exception:
                    logger.debug('{0}: {1}'.format('SQLite', exception))
                    continue
            conn.commit()
            conn.close()
    except Exception as exception:
        logger.debug('{0}: {1}'.format('Exporter', exception))
