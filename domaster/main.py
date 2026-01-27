# MISSION: Hoist yet another to-do manager 'ore Modern Python.
# STATUS: Production
# VERSION: 1.1.3
# NOTES: https://github.com/TotalPythoneering/DoMaster
# DATE: 2026-01-27 10:44:49
# FILE: main.py
# AUTHOR: Randall Nagy
#
import os, sys, shutil
import sqlite3
import uuid
import csv
import datetime

try:
    if '..' not in sys.path:
        sys.path.append('..')
    from domaster.upsert import UpsertSqlite
    from domaster.sync_tool import SQLiteCSVSync
except Exception as ex:
    print(ex)

FILE_ROOT = "domaster.db"
VERSION = "DoMaster 2026.01.27"

class DoMaster:
    def __init__(self, db_file=None):
        self.db_file = None
        self.is_global = True
        if not db_file:
            self.use_global_db()
        else:
            self.use_local_db()
        if not os.path.exists(self.db_file):
            self.init_db()

    def is_db_global(self):
        ''' See if we're using the global database, or no. '''
        return self.is_global

    def use_local_db(self):
        ''' Use the PWD / FOLDER database. '''
        self.db_file = os.path.join(os.getcwd(), FILE_ROOT)
        self.is_global = False

    def use_global_db(self):
        ''' Use the MODULE / GLOBAL database. '''
        root = os.path.dirname(os.path.abspath(__file__))
        self.db_file = os.path.join(root, FILE_ROOT)
        self.is_global = True

    def is_same_db(self):
        ''' Edgy condition - some times they're the same. '''
        a_root = os.path.dirname(os.path.abspath(__file__))
        a_db = os.path.join(a_root, FILE_ROOT)
        b_db = os.path.join(os.getcwd(), FILE_ROOT)
        return a_db == b_db

    def short_db_name(self):
        ''' Print a mnemonic name for the database. '''
        zfile = self.db_file
        if len(zfile) > 25:
            zfile = '...' + zfile[-25:]
        return zfile

    def swap_db(self):
        ''' Toggle GLOBAL database on/off. '''
        if self.is_db_global():
            self.use_local_db()
        else:
            self.use_global_db()
        print(f"Now using {self.short_db_name()} Datbase.")

    def get_fields(self, system=False)->list:
        ''' Manage the two 'flavors' of the files sets. '''
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

    def humanize(self, obj)->list:
        ''' Convert database tags to 'humanized' title-case. '''
        if isinstance(obj, dict):
            return self.humanize(obj.keys())
        elif isinstance(obj, list):
            result = []
            for fld in obj:
                result.append(fld.replace('_', ' ').title())
            return result
        elif isinstance(obj, str):
            return obj.replace('_', ' ').title()
        return obj # gigo
       
    def get_now(self):
        ''' Project `now` time. '''
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def init_db(self):
        ''' Create table if not exist. '''
        conn = sqlite3.connect(self.db_file)
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
        conn.commit()
        conn.close()

    def count(self):
        ''' Count the items in the TODO table. '''
        try:
            conn = sqlite3.connect(self.db_file)
            count_query = f"SELECT COUNT(*) FROM todo;"
            result = conn.execute(count_query)
            tally = int(result.fetchone()[0])
            return tally
        except Exception as ex:
            print(ex)
        finally:
            conn.close()
        return 0

    def add_task(self):
        ''' Add a task to the database. '''
        print("\n--- Add New Task ---")
        proj = input("Project Name: ")
        desc = input("Description: ")
        pri = input("Priority (Integer): ")
        next_t = input("Next Task ID (Default 0): ") or 0
        
        conn = sqlite3.connect(self.db_file)
        conn.execute("""INSERT INTO todo (uuid, project_name, date_created, task_description, task_priority, next_task) 
                     VALUES (?, ?, ?, ?, ?, ?)""", 
                     (str(uuid.uuid4()),
                      proj, self.get_now(),
                      desc, pri, next_t))
        conn.commit()
        conn.close()
        print("Task added successfully.")

    def delete_task(self)->None:
        ''' Remove a task from the database. '''
        if self.count() == 0:
            print("Database is empty.")
            return 0
        tid = input("Enter ID to delete: ").strip()
        if not tid:
            return
        conn = sqlite3.connect(self.db_file)
        conn.execute(f"DELETE FROM todo WHERE ID = ?", (tid))
        conn.commit()
        conn.close()

    def update_task(self)->None:
        ''' Update a task in the database. '''
        if self.count() == 0:
            print("Database is empty.")
            return 0
        tid = input("Enter ID to update: ").strip()
        if not tid:
            return
        fields = self.get_fields()
        fields.remove('ID')
        print("Available fields:")
        for ss, field in enumerate(self.humanize(fields),1):
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
        conn = sqlite3.connect(self.db_file)
        conn.execute(f"UPDATE todo SET {field} = ? WHERE ID = ?", (new_val, tid))
        conn.commit()
        conn.close()

    def mark_done(self):
        ''' Date task ID completed. '''
        tid = input("Enter Task ID to mark as done: ").strip()
        if not tid:
            print("Aborted.")
            return
        conn = sqlite3.connect(self.db_file)
        conn.execute("UPDATE todo SET date_done = ? WHERE ID = ?", (self.get_now(), tid))
        conn.close()

    def list_tasks(self,filter_type="all"):
        print(self.short_db_name())
        fields = self.get_fields()
        query = f"SELECT {', '.join(fields)} FROM todo"
        if filter_type == "pending":
            query += " WHERE date_done IS NULL OR date_done = ''"
        elif filter_type == "done":
            query += " WHERE date_done IS NOT NULL AND date_done != ''"        
        query += " ORDER BY project_name ASC, task_priority ASC"        
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query).fetchall()
        count = 0
        for r in rows:
            count += 1
            print('*'*15)
            print(f"ID      : [{r['ID']:03}]", f"   Next: [{r['next_task']:03}]")
            print(f"Project : [{r['project_name']:<15}]")
            print(f"Priority: [{r['task_priority']:02}]")
            print(f"Created : [{r['date_created']:<15}]")
            print(f"Description: \n\t  [{r['task_description']:<15}]")
        conn.close()
        print(f"View [{filter_type.upper()}] is {count:03} of {self.count():03} items.")

    def export_html(self, status="pending")->int:
        # TODO: Add CSS (et al.)
        ''' Generate the HTML report. Returns number exported. '''
        if self.count() == 0:
            print("Database is empty.")
            return 0
        source = 'global' if self.is_db_global() else 'local'
        filename = f"{source}_report_{status}_{datetime.date.today()}.html"
        fields = self.get_fields()
        sql_fields = ', '.join(fields)
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        if status == "pending":
            rows = conn.execute(f"""SELECT {sql_fields} FROM todo
WHERE date_done IS NULL ORDER BY project_name, task_priority""").fetchall()
            group_field = 'project_name'
        else:
            rows = conn.execute(f"""SELECT {sql_fields} FROM todo
WHERE date_done IS NOT NULL ORDER BY date_done DESC""").fetchall()
            group_field = 'date_done'
        conn.close()

        count = 0
        with open(filename, "w") as f:
            f.write(f"<html><body><h1>DoMaster [{status.upper()}] Report</h1>")
            current_group = None
            for r in rows:
                if r[group_field] != current_group:
                    current_group = r[group_field]
                    f.write(f"<h2>{current_group}</h2>")
                adict = dict(zip(fields, r))
                f.write('<hr>')
                count += 1
                for tag in adict:
                    htag = self.humanize(tag)
                    f.write(f"<b>{htag}:</b>&nbsp;&nbsp;{adict[tag]}<br>")
        print(f"Report exported to {filename}")
        return count

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
        total_pending = self.export_html("pending")
        total_done    = self.export_html("done")
        if total_pending == total_done == 0:
            print("No items exported.")
        else:
            print(f'Pending: {total_pending:03}, Done: {total_done:03}')

    def project_report(self):
        ''' Show all project names. '''
        conn = sqlite3.connect(self.db_file)
        projs = conn.execute("SELECT DISTINCT project_name FROM todo ORDER BY project_name").fetchall()
        for p in projs: print(f"- {p[0]}")
        conn.close()

    def export_csv(self, dated=False)->bool:
        ''' Export to CSV file. '''
        if self.count() == 0:
            print("Database is empty.")
            return False
        mgr = SQLiteCSVSync(self.db_file, 'todo')
        zfile = 'domaster.csv'
        safe = self.get_now().replace(':','-').replace(' ','@')
        if os.path.exists(zfile):
            ztmp = '~' + safe + '_' + zfile
            shutil.copyfile(zfile, ztmp)
            print(f'Saved older {zfile} as {ztmp}.')
        if dated:
            zfile =  f'~domaster_backup_{safe}.csv'
        br = mgr.export_to_csv(zfile)
        if not br:
            print(f"Error: Unable to export {zfile} file.")
        else:
            print(f"Success: Exported {zfile}.")
        return br

    def import_csv(self, file_name=None)->bool:
        ''' Import CSV file into the database. '''
        mgr = SQLiteCSVSync(self.db_file, 'todo')
        zfile = 'domaster.csv'
        if file_name:
            zfile = file_name
        br = mgr.import_from_csv(zfile)
        if not br:
            print(f"Error: Unable to import {zfile} file.")
        else:
            print(f"Success: Imported {zfile}.")
        return br

    def remove_temp_files(self)->None:
        ''' Remove temporary files. '''
        for file in os.listdir():
            if str(file).startswith('~'):
                os.unlink(file)
                if os.path.exists(file):
                    print(f"Warning: Unable to remove {file}.")
                else:
                    print(f"Removed {file}.")

    def backup_and_empty(self)->None:
        ''' Export & reset TODO list. '''
        if self.count() == 0:
            print("Database is empty.")
            return
        cando = input("Okay to blank the database? ").strip().lower()
        if not cando or cando[0] != 'y':
            print("Aborted.")
            return
        if not self.export_csv(True):
            return
        try:
            conn = sqlite3.connect(self.db_file)
            conn.execute("DELETE FROM todo WHERE ID IS NOT 0;")
            conn.commit()
            print("Success: All tasks removed.")
        except Exception as ex:
            print(f"Error: Unable to reset {self.db_file}.")
        finally: conn.close()

    def do_quit(self):
        ''' Exit the program '''
        sys.exit(0)

def mainloop():
    ops = DoMaster()
    line = '=' * len(VERSION)
    print(line,VERSION,line, sep='\n')
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
        'Swap Db':ops.swap_db,
        'Cleanup':ops.remove_temp_files,
        'Quit':ops.do_quit
        }
    keys = list(options.keys())
    times=0
    while True:
        ops.init_db()
        print();selection = None
        zdb = 'Db is [GLOBAL]' if ops.is_db_global() else 'Db is [LOCAL]'
        if ops.is_same_db():
            zdb = 'Db is [SAME]'
        print(zdb)
        print('~'*10)
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
