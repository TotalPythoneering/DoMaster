# MISSION: Manage a to-do list or / and ideas.
# STATUS: Production
# VERSION: 1.1.1
# NOTES: Tested. See the project for full documentation.
# DATE: 2026-01-27 08:38:38
# FILE: sync_tool.py
# AUTHOR: Randall Nagy
#
''' Generative:
create a python program to export as well as to import
a sqlite database table to a csv file. Assume the
existence of a 'uuid' column in each database row
to manage the database table's insertion or update
of any row.

in addition to the unique uuid field the other fields
are to be automatically detected from the SQLite
format's metadata for the table. include a robust
set of test cases.
'''
import os, sys
import csv, uuid
import sqlite3

try:
    if '..' not in sys.path:
        sys.path.insert(0,'..')
    from domaster.upsert import UpsertSqlite
except Exception as ex:
    pass

class SQLiteCSVSync:
    def __init__(self, db_path, table_name):
        self.db_path = db_path
        self.table_name = table_name

    def _get_column_names(self):
        """Automatically detects table column names from metadata."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # PRAGMA table_info returns (id, name, type, notnull, default_value, pk)
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns = [info[1] for info in cursor.fetchall()]
            if not columns:
                raise ValueError(f"Table '{self.table_name}' not found or empty.")
            return UpsertSqlite.JunkId(columns)

    def export_to_csv(self, csv_file)->bool:
        """ Export all data from the detected table to a CSV file.
            Return True on success.
        """
        columns = self._get_column_names()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {', '.join(columns)} FROM {self.table_name}")
            rows = cursor.fetchall()

            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns) # Header
                writer.writerows(rows)
        return os.path.exists(csv_file)

    def import_from_csv(self, csv_file)->int:
        """ Import CSV data using 'uuid' as the key for UPSERT logic.
            Returns the number of rows imported.
        """
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file '{csv_file}' not found.")

        columns = self._get_column_names()
        if 'uuid' not in columns:
            raise ValueError("Table must have a 'uuid' column for synchronization.")

        # Create a uuid for any lacking same.
        inventory = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row['uuid']:
                    row['uuid'] = uuid.uuid4()
                inventory.append(row)

        # Approve effect of data imporatation.
        conn = sqlite3.connect(self.db_path)
        new_rows = 0; old_rows = 0
        for row in inventory:
            next_t = row['uuid']
            res = conn.execute(f'SELECT * FROM todo WHERE uuid = "{next_t}" LIMIT 1;')
            if res:
                old_rows += 1
            else:
                new_rows += 1
        conn.close()
        yn = input(f'Ok to update {old_rows} and create {new_rows} todo items? y/n ').strip().lower()
        if not yn or yn[0] != 'y':
            print('Aborted.')
            return -1
        print("Updating database ...")
        
        # Dynamic UPSERT query construction
        placeholders = ", ".join(["?"] * len(columns))
        col_list = ", ".join(columns)
        update_set = ", ".join([f"{col} = excluded.{col}" for col in columns if col != 'uuid'])
        upsert_sql = f"""
            INSERT INTO {self.table_name} ({col_list})
            VALUES ({placeholders})
            ON CONFLICT(uuid) DO UPDATE SET {update_set}
        """
        with sqlite3.connect(self.db_path) as conn:
            data = [tuple(row[col] for col in columns) for row in inventory]
            conn.executemany(upsert_sql, data)
            conn.commit()
        return len(data)
