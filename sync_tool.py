# MISSION: Manage a to-do list or / and ideas.
# STATUS: Research
# VERSION: 0.0.0
# NOTES: Lighty tested. See the project for full documentation.
# DATE: 2026-01-24 09:06:19
# FILE: sync_tool.py
# AUTHOR: Randall Nagy
#
''' Generative:
create a python program to export as well as to import
a sqlite database table to a csv file. Assume the
existence of a 'guid' column in each database row
to manage the database table's insertion or update
of any row.

in addition to the unique guid field the other fields
are to be automatically detected from the SQLite
format's metadata for the table. include a robust
set of test cases.
'''
import sqlite3
import csv
import os

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
            return columns

    def export_to_csv(self, csv_file):
        """Exports all data from the detected table to a CSV file."""
        columns = self._get_column_names()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name}")
            rows = cursor.fetchall()

            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns) # Header
                writer.writerows(rows)
        return len(rows)

    @staticmethod
    def EncodeUpsertSet(table_name: str, row: dict) -> tuple:
        ''' Generates a parameterized UPSERT string
            and its associated values. This version
            generates a safe SQL string with ?
            placeholders and returns both the query
            and the data tuple.

        Why this is better for your 2026 project:
            * SQL Injection Protection: By using ?
            placeholders, the database engine handles
            the sanitization of strings, preventing
            malicious code injection.

            * Type Handling: SQLite will correctly handle
            None (NULL), integers, and floats without you
            having to manually format them into a string.
            
            * Efficiency: Parameterized queries allow the
            SQLite engine to "compile" the query once and
            reuse the plan, which is faster for bulk imports.
            
            * Special Characters: It correctly handles quotes,
            backslashes, and emojis within your address or name
            fields that would otherwise break a raw string.
'''
        if 'guid' not in row:
            raise ValueError(f"Table [{table_name}] missing 'guid' column.")
        
        column_names = ", ".join(row.keys())
        # Create placeholders like (?, ?, ?)
        placeholders = ", ".join(["?"] * len(row))
        
        # Create the update clause: col1 = excluded.col1, col2 = excluded.col2...
        update_set = ", ".join(
            [f"{col} = excluded.{col}" for col in row if col != 'guid']
        )

        upsert_sql = f"""
            INSERT INTO {table_name} ({column_names})
            VALUES ({placeholders})
            ON CONFLICT(guid) DO UPDATE SET {update_set}
        """
        
        # Return both the query and the values to be
        # passed to cursor.execute()
        return upsert_sql, tuple(row.values())


    @staticmethod
    def EncodeUpsert(table_name:str, row:dict)->str:
        ''' Encode a dynamic UPSERT ON CONFLICT clause. '''
        if 'guid' not in row:
            raise ValueError(
                f"Table [{table_name}] missing 'guid' column.")
        placeholders = ", ".join(["?"] * len(row))
        column_names = ", ".join(row.keys())
        insert_values = tuple(row.values())
        update_set = ", ".join(
            [f"{col} = excluded.{col}" for col in row if col != 'guid'])

        upsert_sql = f"""
            INSERT INTO {table_name} ({column_names})
            VALUES {insert_values}
            ON CONFLICT(guid) DO UPDATE SET {update_set}
        """
        return upsert_sql


    def import_from_csv(self, csv_file):
        """Imports CSV data using 'guid' as the key for UPSERT logic."""
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file '{csv_file}' not found.")

        columns = self._get_column_names()
        if 'guid' not in columns:
            raise ValueError("Table must have a 'guid' column for synchronization.")

        # Dynamic UPSERT query construction
        placeholders = ", ".join(["?"] * len(columns))
        col_list = ", ".join(columns)
        update_set = ", ".join([f"{col} = excluded.{col}" for col in columns if col != 'guid'])

        upsert_sql = f"""
            INSERT INTO {self.table_name} ({col_list})
            VALUES ({placeholders})
            ON CONFLICT(guid) DO UPDATE SET {update_set}
        """

        with sqlite3.connect(self.db_path) as conn:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                # Map CSV rows to tuple based on detected column order
                data = [tuple(row[col] for col in columns) for row in reader]
                conn.executemany(upsert_sql, data)
                conn.commit()
        return len(data)
