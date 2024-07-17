#!/usr/bin/env python3
import datetime
import exporter
import indexeddb_util
import logger

def classify_records(data, raw_records, global_metadata, database_metadata, object_store_metadata):
        metadata = []
        origin = ''
        for db_info in global_metadata.db_ids:
            origin = db_info.origin
            max_objstore_id = database_metadata.get_meta(db_info.dbid_no, indexeddb_util.DatabaseMetadataType.MaximumObjectStoreId)
            for obj_store_id in range(1, max_objstore_id + 1):
                obj_store_name =object_store_metadata.get_meta(db_info.dbid_no, obj_store_id, indexeddb_util.ObjectStoreMetadataType.StoreName)
                metadata.append((db_info.dbid_no, db_info.name, obj_store_id, obj_store_name))
        
        if origin:
            origin = origin.split('@')[0] + '.db'
        else:
            local_date_time = datetime.datetime.now()
            origin = (
                    '{0:s}-{1:04d}{2:02d}{3:02d}.db').format(
                    'Unknown', local_date_time.year, local_date_time.month,
                    local_date_time.day)
        try:
            if len(metadata) > 0:
                if not exporter.check_table_exists(origin, 'Metadata'):
                    exporter.create_table(origin, None, exporter.TABLE_TYPE.Metadata)
                for table in metadata:
                    exporter.create_table(origin, table[1].replace(':', '_').replace('-', '_').replace(' ', '_'), exporter.TABLE_TYPE.Data)
                exporter.insert_records(origin, metadata, exporter.DATA_TYPE.Metadata)
                
            if len(data) > 0:
                if not exporter.check_table_exists(origin, 'Metadata'):
                    exporter.create_table(origin, None, exporter.TABLE_TYPE.Metadata)
                if not exporter.check_table_exists(origin, 'Unclassified'):
                    exporter.create_table(origin, None, exporter.TABLE_TYPE.Unclassified)
                exporter.insert_records(origin, data, exporter.DATA_TYPE.IndexedDBData)

            if len(raw_records) > 0 and len(data) == 0:
                if not exporter.check_table_exists(origin, 'Unclassified'):
                    exporter.create_table(origin, None, exporter.TABLE_TYPE.Unclassified)
                exporter.insert_records(origin, raw_records, exporter.DATA_TYPE.LevelDBData)
        except Exception as exception:
            logger.debug('{0}: {1}'.format('SQLite', exception))