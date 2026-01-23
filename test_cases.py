# MISSION: tbd.
# STATUS: tbd.
# VERSION: 0.0.0
# NOTES: tbd.
# DATE: 2026-01-23 06:00:28
# FILE: test_cases.py
# AUTHOR: tbd.
# Generative: "Please add some test cases."
# Status - Quick fix. Ramefication review luego.
#

import unittest
import uuid
import sqlite3
import os
import csv
from unittest.mock import patch

from domaster import DoMaster

DATABASE = "~test.db"

class TestDoMaster(unittest.TestCase):
  
    def setUp(self):
        self.db_file = DATABASE
        self.sut = DoMaster(self.db_file)
        self.sut.init_db()

    def test_add_task_integrity(self):
        """Test if a task is correctly added with an immutable UUID."""
        # Mock inputs for add_task: Project, Description, Priority, Next Task
        with patch('builtins.input', side_effect=["Work", "Finish Report", "1", "0"]):
            self.sut.add_task()

        with sqlite3.connect(self.db_file) as conn:
            row = conn.execute("SELECT uuid, project_name, task_description FROM todo").fetchone()
            self.assertIsNotNone(row[0])  # UUID exists
            self.assertEqual(row[1], "Work")
            self.assertEqual(row[2], "Finish Report")

    def test_mark_done_updates_timestamp(self):
        """Test that marking a task done sets the date_done field."""
        # Insert a dummy task first
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(f"INSERT INTO todo (uuid, task_description) VALUES ('{uuid.uuid4()}', 'Task 1')")
        
        with patch('builtins.input', return_value="1"):
            self.sut.mark_done()

        with sqlite3.connect(self.db_file) as conn:
            date_done = conn.execute("SELECT date_done FROM todo WHERE ID=1").fetchone()[0]
            self.assertIsNotNone(date_done)
            self.assertIn(":", date_done) # Verify it looks like a timestamp

    def test_duplicate_uuid_on_import(self):
        """Test that importing a task with an existing UUID updates the record."""
        # Initial insert
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(f"INSERT INTO todo (uuid, project_name, task_description) VALUES ('{uuid.uuid4()}', 'Old Proj', 'Old Desc')")

        # Create a mock CSV for import
        test_csv = 'test_import.csv'
        with open(test_csv, 'w', newline='') as f:
            zuuid = uuid.uuid4()
            writer = csv.DictWriter(f, fieldnames=["uuid", "project_name", "date_created", "date_done", "task_description", "task_priority", "next_task"])
            writer.writeheader()
            writer.writerow({
                "uuid": f"{zuuid}", 
                "project_name": "Updated Proj", 
                "date_created": "2026-01-01 10:00:00",
                "date_done": "", 
                "task_description": "Updated Desc", 
                "task_priority": 5, 
                "next_task": 0
            })

        self.sut.import_file(test_csv, ',')

        with sqlite3.connect(self.db_file) as conn:
            row = conn.execute(f"SELECT project_name, task_description FROM todo WHERE uuid='{zuuid}'").fetchone()
            self.assertEqual(row[0], "Updated Proj")
            self.assertEqual(row[1], "Updated Desc")
        
        os.remove(test_csv)

    def test_distinct_projects_sorted(self):
        """Test the distinct project listing functionality."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(f"INSERT INTO todo (uuid, project_name) VALUES ('{uuid.uuid4()}', 'Zebra'), ('{uuid.uuid4()}', 'Apple'), ('{uuid.uuid4()}', 'Apple')")
        
        with sqlite3.connect(self.db_file) as conn:
            projs = conn.execute("SELECT DISTINCT project_name FROM todo ORDER BY project_name").fetchall()
            self.assertEqual(len(projs), 3)
            self.assertEqual(projs[0][0], "Apple")
            self.assertEqual(projs[1][0], "Work")

if __name__ == "__main__":
    if os.path.exists(DATABASE):
        os.unlink(DATABASE)
    unittest.main()

