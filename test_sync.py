# MISSION: Manage a to-do list or / and ideas.
# STATUS: Research
# VERSION: 0.0.0
# NOTES: Lighty tested. See the project for full documentation.
# DATE: 2026-01-24 09:06:36
# FILE: test_sync.py
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
import unittest
import sqlite3
import csv
import os
import time
from sync_tool import SQLiteCSVSync

class TestSync(unittest.TestCase):
    DB = "test_data.db"
    CSV = "test_data.csv"

    def setUp(self):
        # Create fresh table for testing
        with sqlite3.connect(self.DB) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS contacts (
                guid TEXT PRIMARY KEY, name TEXT, age TEXT, phone TEXT
            )""")
        self.sync = SQLiteCSVSync(self.DB, "contacts")

    def tearDown(self):
        """Safely remove files with a retry for Windows file locks."""
        for file in [self.DB, self.CSV]:
            if os.path.exists(file):
                for _ in range(5): # Retry 5 times
                    try:
                        os.remove(file)
                        break
                    except PermissionError:
                        time.sleep(0.1)

    def test_export_logic(self):
        """Verify metadata detection and data export."""
        data = {
            'guid':'g1',
            'name':'Alice',
            'age':'30',
            'phone':'555'
            }
        cmd = SQLiteCSVSync.EncodeUpsert('contacts', data)
        print(cmd)
        with sqlite3.connect(self.DB) as conn:
            conn.execute(cmd)
        
        self.sync.export_to_csv(self.CSV)
        with open(self.CSV, 'r') as f:
            reader = list(csv.reader(f))
            self.assertEqual(reader[0], ['guid', 'name', 'age', 'phone'])
            self.assertEqual(reader[1], ['g1', 'Alice', '30', '555'])

    def test_upsert_logic(self):
        """Verify 'guid' allows both updating existing and inserting new rows."""
        data = {
            'guid':'g1',
            'name':'Old',
            'age':'20',
            'phone':'000'
            }
        cmd = SQLiteCSVSync.EncodeUpsert('contacts', data)
        print(cmd)
        with sqlite3.connect(self.DB) as conn:
            conn.execute(cmd)
        
        with open(self.CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['guid', 'name', 'age', 'phone'])
            writer.writerow(['g1', 'New', 21, '111']) # Update g1
            writer.writerow(['g2', 'Bob', 40, '222']) # New g2

        self.sync.import_from_csv(self.CSV)

        with sqlite3.connect(self.DB) as conn:
            upd = conn.execute("SELECT name FROM contacts WHERE guid='g1'").fetchone()[0]
            ins = conn.execute("SELECT name FROM contacts WHERE guid='g2'").fetchone()[0]
            self.assertEqual(upd, "New")
            self.assertEqual(ins, "Bob")

    def test_schema_agnostic(self):
        """Verify automatic detection of a completely different table schema."""
        with sqlite3.connect(self.DB) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS products (guid TEXT PRIMARY KEY, price REAL)")
        
        p_sync = SQLiteCSVSync(self.DB, "products")
        with open(self.CSV, 'w', newline='') as f:
            f.write("guid,price\np1,19.99")
        
        p_sync.import_from_csv(self.CSV)
        with sqlite3.connect(self.DB) as conn:
            res = conn.execute("SELECT price FROM products").fetchone()[0]
            self.assertEqual(res, 19.99)

if __name__ == "__main__":
    unittest.main()
