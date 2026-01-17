# Generative: "Please add some test cases."

import unittest
import sqlite3
import os
import csv
from unittest.mock import patch
# Assuming the main file is named domaster.py
import domaster 

class TestDoMaster(unittest.TestCase):
    def setUp(self):
        """Initialize an in-memory database for each test."""
        # Override the global DB_NAME for testing
        domaster.DB_NAME = ":memory:"
        domaster.init_db()

    def test_add_task_integrity(self):
        """Test if a task is correctly added with an immutable UUID."""
        # Mock inputs for add_task: Project, Description, Priority, Next Task
        with patch('builtins.input', side_effect=["Work", "Finish Report", "1", "0"]):
            domaster.add_task()

        with sqlite3.connect(domaster.DB_NAME) as conn:
            row = conn.execute("SELECT uuid, project_name, task_description FROM todo").fetchone()
            self.assertIsNotNone(row[0])  # UUID exists
            self.assertEqual(row[1], "Work")
            self.assertEqual(row[2], "Finish Report")

    def test_mark_done_updates_timestamp(self):
        """Test that marking a task done sets the date_done field."""
        # Insert a dummy task first
        with sqlite3.connect(domaster.DB_NAME) as conn:
            conn.execute("INSERT INTO todo (ID, uuid, task_description) VALUES (1, 'test-uuid', 'Task 1')")
        
        with patch('builtins.input', return_value="1"):
            domaster.mark_done()

        with sqlite3.connect(domaster.DB_NAME) as conn:
            date_done = conn.execute("SELECT date_done FROM todo WHERE ID=1").fetchone()[0]
            self.assertIsNotNone(date_done)
            self.assertIn(":", date_done) # Verify it looks like a timestamp

    def test_duplicate_uuid_on_import(self):
        """Test that importing a task with an existing UUID updates the record."""
        # Initial insert
        with sqlite3.connect(domaster.DB_NAME) as conn:
            conn.execute("INSERT INTO todo (uuid, project_name, task_description) VALUES ('same-uuid', 'Old Proj', 'Old Desc')")

        # Create a mock CSV for import
        test_csv = 'test_import.csv'
        with open(test_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["uuid", "project_name", "date_created", "date_done", "task_description", "task_priority", "next_task"])
            writer.writeheader()
            writer.writerow({
                "uuid": "same-uuid", 
                "project_name": "Updated Proj", 
                "date_created": "2026-01-01 10:00:00",
                "date_done": "", 
                "task_description": "Updated Desc", 
                "task_priority": 5, 
                "next_task": 0
            })

        domaster.import_file(test_csv, ',')

        with sqlite3.connect(domaster.DB_NAME) as conn:
            row = conn.execute("SELECT project_name, task_description FROM todo WHERE uuid='same-uuid'").fetchone()
            self.assertEqual(row[0], "Updated Proj")
            self.assertEqual(row[1], "Updated Desc")
        
        os.remove(test_csv)

    def test_distinct_projects_sorted(self):
        """Test the distinct project listing functionality."""
        with sqlite3.connect(domaster.DB_NAME) as conn:
            conn.execute("INSERT INTO todo (uuid, project_name) VALUES ('1', 'Zebra'), ('2', 'Apple'), ('3', 'Apple')")
        
        with sqlite3.connect(domaster.DB_NAME) as conn:
            projs = conn.execute("SELECT DISTINCT project_name FROM todo ORDER BY project_name").fetchall()
            self.assertEqual(len(projs), 2)
            self.assertEqual(projs[0][0], "Apple")
            self.assertEqual(projs[1][0], "Zebra")

if __name__ == "__main__":
    unittest.main()
