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
import csv
import sqlite3

try:
    if '..' not in sys.path:
        sys.path.append('..')
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

    def import_from_csv(self, csv_file):
        """ Import CSV data using 'uuid' as the key for UPSERT logic.
            Returns the number of rows imported.
        """
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file '{csv_file}' not found.")

        columns = self._get_column_names()
        if 'uuid' not in columns:
            raise ValueError("Table must have a 'uuid' column for synchronization.")
        
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
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                # Map CSV rows to tuple based on detected column order
                data = [tuple(row[col] for col in columns) for row in reader]
                conn.executemany(upsert_sql, data)
                conn.commit()
        return len(data)
