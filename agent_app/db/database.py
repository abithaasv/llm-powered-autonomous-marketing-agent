import os
import lancedb
from db.schemas import schemas

import logging

# Get the logger for the current module
logger = logging.getLogger(__name__)

def setup_db():
    # LanceDB setup
    VECTOR_DB_DIR = os.environ.get("VECTOR_DATABASE_DIRECTORY")

    if not os.path.exists(VECTOR_DB_DIR):
        os.mkdir(VECTOR_DB_DIR)

    uri = VECTOR_DB_DIR
    db = lancedb.connect(uri)

    return db

def push_to_db(db, table_name, data):

    # create the table if not exists
    if table_name not in db.table_names():
        db.create_table(table_name, schema=schemas[table_name])
    
    table = db.open_table(table_name)
    table.add(data=data)

    return "success"

def delete_table(tablename):
    db = setup_db()
    db.drop_table(tablename)

    return True

def clear_db(db):
    # Drop all the tables
    for db_name in db.table_names():
        db.drop_table(db_name)

    return True

def get_all_table_records(table_name):
    db = setup_db()

    table = db.open_table(table_name)

    records_df = (table.search()
                   .to_pandas()
                   )
    
    return records_df


def get_table_record(table_name, record_id):
    db = setup_db()

    table = db.open_table(table_name)

    record_df = (table.search()
                  .where(f"id = '{record_id}'", prefilter=True)
                   .to_pandas()
                   )
    
    return record_df
