# MISSION: Hoist yet another to-do manager 'ore Modern Python.
# STATUS: Research
# VERSION: 0.0.1
# NOTES: Google's A.I only did so much - we've a few more things to add.
# DATE: 2026-01-23 06:51:54
# FILE: domaster.py
# AUTHOR: Randall Nagy
#
import os, sys
import sqlite3
import uuid
import csv
import datetime

VERSION = "DoMaster 0.0.1"
DB_NAME = "domaster.db"

class DoMaster:
    def __init__(self, db_file=DB_NAME):
        self.db_file = db_file
    def get_now(self):
        ''' Project `now` time. '''
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def init_db(self):
        ''' Create table if not exist. '''
        print(self.db_file)
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS todo (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT UNIQUE,
                    project_name TEXT,
                    date_created TEXT,
                    date_done TEXT,
                    task_description TEXT,
                    task_priority INTEGER,
                    next_task INTEGER DEFAULT 0
                )
            """)

    def add_task(self):
        ''' Add a task to the database. '''
        print("\n--- Add New Task ---")
        proj = input("Project Name: ")
        desc = input("Description: ")
        pri = input("Priority (Integer): ")
        next_t = input("Next Task ID (Default 0): ") or 0
        
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""INSERT INTO todo (uuid, project_name, date_created, task_description, task_priority, next_task) 
                         VALUES (?, ?, ?, ?, ?, ?)""", 
                         (str(uuid.uuid4()), proj, self.get_now(), desc, pri, next_t))
        print("Task added successfully.")

    def update_task(self):
        ''' Update a task in the database. '''
        tid = input("Enter ID to update: ")
        fields = ["project_name", "task_description", "task_priority", "next_task", "date_done"]
        print("Available fields:", ", ".join(fields))
        field = input("Field to update: ")
        new_val = input(f"New value for {field}: ")
        
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(f"UPDATE todo SET {field} = ? WHERE ID = ?", (new_val, tid))

    def mark_done(self):
        ''' Complete a task in the database. '''
        tid = input("Enter Task ID to mark as done: ")
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("UPDATE todo SET date_done = ? WHERE ID = ?", (self.get_now(), tid))

    def list_tasks(self,filter_type="all"):
        query = "SELECT ID, project_name, task_description, task_priority, date_created, date_done FROM todo"
        if filter_type == "pending": query += " WHERE date_done IS NULL OR date_done = ''"
        elif filter_type == "done": query += " WHERE date_done IS NOT NULL AND date_done != ''"
        
        query += " ORDER BY project_name ASC, task_priority ASC"
        
        with sqlite3.connect(self.db_file) as conn:
            rows = conn.execute(query).fetchall()
            print(f"\n{'ID':<4} | {'Project':<15} | {'Description':<25} | {'Pri':<4} | {'Created'}")
            print("-" * 80)
            for r in rows:
                print(f"{r[0]:<4} | {r[1]:<15} | {r[2]:<25} | {r[3]:<4} | {r[4]}")

    def export_html(self, status="pending"):
        ''' Generate the HTML report. '''
        filename = f"report_{status}_{datetime.date.today()}.html"
        with sqlite3.connect(self.db_file) as conn:
            if status == "pending":
                rows = conn.execute("SELECT project_name, task_description, task_priority, date_created FROM todo WHERE date_done IS NULL ORDER BY project_name, task_priority").fetchall()
                group_field = 0 # project_name
            else:
                rows = conn.execute("SELECT date_done, project_name, task_description, task_priority FROM todo WHERE date_done IS NOT NULL ORDER BY date_done DESC").fetchall()
                group_field = 0 # date_done

        with open(filename, "w") as f:
            f.write(f"<html><body><h1>DoMaster {status.capitalize()} Report</h1>")
            current_group = None
            for r in rows:
                if r[group_field] != current_group:
                    current_group = r[group_field]
                    f.write(f"<h2>{current_group}</h2>")
                f.write(f"<p>{r[1]} - Priority: {r[2]} (Created: {r[3] if status=='pending' else ''})</p>")
            f.write("</body></html>")
        print(f"Report exported to {filename}")

    def import_file(self, filename, delimiter):
        ''' Import a database export. '''
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            with sqlite3.connect(self.db_file) as conn:
                for row in reader:
                    conn.execute("""
                        INSERT INTO todo (uuid, project_name, date_created, date_done, task_description, task_priority, next_task)
                        VALUES (:uuid, :project_name, :date_created, :date_done, :task_description, :task_priority, :next_task)
                        ON CONFLICT(uuid) DO UPDATE SET
                            project_name=excluded.project_name,
                            date_done=excluded.date_done,
                            task_description=excluded.task_description,
                            task_priority=excluded.task_priority,
                            next_task=excluded.next_task
                    """, row)

    def list_pending(self):
        ''' List pending tasks. '''
        self.list_tasks("pending")

    def list_done(self):
        ''' List completed tasks. '''
        self.list_tasks("done")

    def list_all(self):
        ''' List all tasks. '''
        self.list_tasks("all")

    def html_report(self):
        ''' Create the HTML Report. '''
        self.export_html("pending")
        self.export_html("done")

    def project_report(self):
        ''' Show all project names. '''
        with sqlite3.connect(self.db_file) as conn:
            projs = conn.execute("SELECT DISTINCT project_name FROM todo ORDER BY project_name").fetchall()
            for p in projs: print(f"- {p[0]}")

    def todo(self):
        ''' Unloved - work in progress '''
        print("Work in progress - stay tuned?")

    def do_quit(self):
        ''' Exit the program '''
        sys.exit(0)

def mainloop():
    ops = DoMaster()
    line = '=' * len(VERSION)
    print(line,VERSION,line, sep='\n')
    ops.init_db()
    options = {
        'Add Task':ops.add_task,
        'Update Task':ops.update_task,
        'Tack Complete':ops.mark_done,
        'List Pendings':ops.list_pending,
        'List Done':ops.list_done,
        'List All':ops.list_all,
        'Projects':ops.project_report,
        'HTML Report':ops.html_report,
        'Export Data':ops.todo,
        'Import Data':ops.todo,
        'Database Backup':ops.todo,
        'Quit':ops.do_quit
        }
    keys = list(options.keys())
    times=0
    while True:
        print();selection = None
        for ss, op in enumerate(keys, 1):
            tag = f'{op}:'
            print(f'{ss:02}.) {tag:<18}{options[op].__doc__}')
        try:
            selection = input("Enter #: ")
            which = int(selection.strip())
            if which > 0 and which <= len(keys):
                times = 0
                selection = keys[which-1]
                if selection in options: # double check
                    print('*'*which, selection)
                    options[selection]()
            else:
                print(f"Invalid number {which}.")
        except Exception as ex:
            times += 1
            if times > 12:
                print("I've no time for this - bye!")
                ops.do_quit()
            print(ex)
            print("Numbers only, please.")
            continue

if __name__ == "__main__":
    mainloop()
