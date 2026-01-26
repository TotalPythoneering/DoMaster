# MISSION: Hoist yet another to-do manager 'ore Modern Python.
# STATUS: Research
# VERSION: 0.2.1
# NOTES: Google's A.I only did so much - we've a few more things to add.
# DATE: 2026-01-26 10:57:22
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

    def get_fields(self, system=False)->list:
        results = [
                    'ID',
                    'uuid',
                    'project_name',
                    'date_created',
                    'date_done',
                    'task_description',
                    'task_priority',
                    'next_task'
            ]
        if not system:
            results.remove('uuid')
        return results
        
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
            conn.commit()
        print("Task added successfully.")

    def delete_task(self):
        ''' Remove a task from the database. '''
        tid = input("Enter ID to delete: ").strip()
        if not tid:
            return
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(f"DELETE FROM todo WHERE ID = ?", (tid))
            conn.commit()

    def update_task(self):
        ''' Update a task in the database. '''
        tid = input("Enter ID to update: ").strip()
        if not tid:
            return
        fields = self.get_fields()
        fields.remove('ID')
        print("Available fields:")
        for ss, field in enumerate(fields,1):
            print(f'{ss:02}.) {field}') 
        which = input("Field # to update: ").strip()
        if not which:
            return
        try:
            which = int(which)
            which -= 1
            field = fields[which]
        except:
            print("Invalid field number.")
            return
        del which
        new_val = input(f"New value for {field}: ").strip()
        if not new_val:
            print("Aborted.")
            return
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(f"UPDATE todo SET {field} = ? WHERE ID = ?", (new_val, tid))
            conn.commit()

    def mark_done(self):
        ''' Date task ID completed. '''
        tid = input("Enter Task ID to mark as done: ").strip()
        if not tid:
            print("Aborted.")
            return
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("UPDATE todo SET date_done = ? WHERE ID = ?", (self.get_now(), tid))

    def list_tasks(self,filter_type="all"):
        fields = self.get_fields()
        query = f"SELECT {', '.join(fields)} FROM todo"
        if filter_type == "pending":
            query += " WHERE date_done IS NULL OR date_done = ''"
        elif filter_type == "done":
            query += " WHERE date_done IS NOT NULL AND date_done != ''"        
        query += " ORDER BY project_name ASC, task_priority ASC"        
        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query).fetchall()
            for r in rows:
                print('*'*15)
                print(f"ID      : [{r['ID']:03}]", f"   Next: [{r['next_task']:03}]")
                print(f"Project : [{r['project_name']:<15}]")
                print(f"Priority: [{r['task_priority']:02}]")
                print(f"Created : [{r['date_created']:<15}]")
                print(f"Description: \n\t  [{r['task_description']:<15}]")

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

    def export_csv(self, dated=False)->bool:
        ''' Export to CSV file. '''
        from sync_tool import SQLiteCSVSync
        mgr = SQLiteCSVSync(self.db_file, 'todo')
        zfile = self.db_file + '.csv'
        if dated:
            zfile = self.get_now().replace(':','-').replace(' ','@') + '_' + zfile
        br = mgr.export_to_csv(zfile)
        if not br:
            print(f"Error: Unable to export {zfile} file.")
        else:
            print(f"Success: Exported {zfile}.")
        return br

    def import_csv(self, file_name=None)->bool:
        ''' Import CSV file into the database. '''
        from sync_tool import SQLiteCSVSync
        mgr = SQLiteCSVSync(self.db_file, 'todo')
        zfile = self.db_file + '.csv'
        if file_name:
            zfile = file_name
        br = mgr.import_from_csv(zfile)
        if not br:
            print(f"Error: Unable to import {zfile} file.")
        else:
            print(f"Success: Imported {zfile}.")
        return br

    def backup_and_empty(self)->None:
        ''' Export & reset TODO list. '''
        if not self.export_csv(True):
            return
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.execute("DELETE FROM todo WHERE ID IS NOT 0;")
                conn.commit()
                print("Success: All tasks removed.")
        except Exception as ex:
            print(f"Error: Unable to reset {self.db_file}.")

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
        'Delete Task':ops.delete_task,
        'Update Task':ops.update_task,
        'Mark Completed':ops.mark_done,
        'List Pendings':ops.list_pending,
        'List Done':ops.list_done,
        'List All':ops.list_all,
        'Projects':ops.project_report,
        'HTML Report':ops.html_report,
        'Export Data':ops.export_csv,
        'Import Data':ops.import_csv,
        'Reset Database':ops.backup_and_empty,
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
