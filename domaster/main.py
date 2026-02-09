# MISSION: Hoist yet another to-do manager 'ore Modern Python.
# STATUS: Production
# VERSION: 3.0.0
# NOTES: https://github.com/TotalPythoneering/DoMaster
# DATE: 2026-02-08 11:07:12
# FILE: main.py
# AUTHOR: Randall Nagy
#
import os, sys, shutil
from pathlib import Path
import sqlite3
import uuid
import csv
import datetime

if '..' not in sys.path:
    sys.path.insert(0, '..')
from domaster.upsert import UpsertSqlite
from domaster.tui_loop import Loop
from domaster.manage_files import ManageFiles
from domaster.manage_archive import ManageArchived

from domaster.keeper import Keeps

APP_NAME  = "DoMaster"
FILE_TYPE = ".db"
FILE_ROOT = "domaster" + FILE_TYPE
VERSION   = APP_NAME + " 2026.02.07"
DATA_TYPE = ".options"

class DoMaster(Loop):
    def __init__(self, db_file=None):
        super().__init__()
        self.db_file = None
        self.is_global = True
        if not db_file:
            self.use_global_db()
        else:
            self.use_local_db()
        if not os.path.exists(self.db_file):
            self.init_db()

    def do_quit(self):
        ''' Quit DoMaster '''
        if Keeps.get_option('auto_backup'):
            util = ManageArchived(self)
            if util.create_archive():
                print("Success: Backup created.")
            else:
                print("Warning: Auto backup failure.")
        super().do_quit()

    def loop_status(self, **kwargs):
        if kwargs['errors'] > 12:
            print('Too many errors.')
            self.do_quit()
            return
        self.init_db()
        print()
        zdb = 'Db is [GLOBAL]' if self.is_db_global() else 'Db is [LOCAL]'
        if self.is_same_db():
            zdb = 'Db is [SAME]'
        print(zdb)
        print('~'*10)

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
        if len(zfile) > 40:
            zfile = '...' + zfile[-40:]
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
                next_task TEXT
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
        pri = self.get_int("Priority (Integer): ")
        next_t = self.get_int("Next Task ID (Default 0): ")
        if next_t:
            ref_task = self.read_row_for_id(next_t)
            if ref_task:
                next_t = ref_task['uuid']
            else:
                print(f"Task #{next_t} not found. Set to Zero.")
                next_t = 0
        
        conn = sqlite3.connect(self.db_file)
        conn.execute("""INSERT INTO todo (uuid, project_name, date_created, task_description, task_priority, next_task) 
                     VALUES (?, ?, ?, ?, ?, ?)""", 
                     (str(uuid.uuid4()),
                      proj, self.get_now(),
                      desc, pri, next_t))
        conn.commit()
        conn.close()
        print("Task added successfully.")

    def read_row_for_uuid(self, next_t:str)->dict:
        ''' Lookup a task by uuid. None if not found. '''
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            res = conn.execute(f'SELECT * FROM todo WHERE uuid = "{next_t}" LIMIT 1;')
            if res:
                return dict(res.fetchone())
        except:
            pass
        finally:
            conn.close()
        return None

    def read_row_for_id(self, next_t:int)->dict:
        ''' Lookup a task by primary key. None if not found. '''
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            res = conn.execute(f'SELECT * FROM todo WHERE ID = {next_t} LIMIT 1;')
            if res:
                return dict(res.fetchone())
        except:
            pass
        finally:
            conn.close()
        return None

    def delete_task(self)->None:
        ''' Remove a task from the database. '''
        if self.count() == 0:
            print("Database is empty.")
            return 0
        self.show_task_numbers()
        tid = self.get_int("Enter ID to delete: ")
        if not tid:
            return
        conn = sqlite3.connect(self.db_file)
        conn.execute(f"DELETE FROM todo WHERE ID = {tid}")
        conn.commit()
        conn.close()

    def display(self, row):
        if not row:
            print("Unable to display [{row}].")
            return
        print('~'*15)
        print(f"ID      : [{row['ID']}]", f"   Next: [{row['next_task']}]")
        print(f"Project : [{row['project_name']}]")
        print(f"Priority: [{row['task_priority']}]")
        print(f"Created : [{row['date_created']}]")
        print(f"Description: \n\t  [{row['task_description']}]")

    def display_task_id(self, tid)->bool:
        a_row = self.read_row_for_id(tid)
        if not a_row:
            print(f"No task @[{tid}].")
            return False
        self.display(a_row)
        return True

    def update_task(self)->None:
        ''' Update a task in the database. '''
        if self.count() == 0:
            print("Database is empty.")
            return 0
        self.show_task_numbers()
        tid = self.get_int("Enter ID to update: ")
        if not tid:
            return
        fields = self.get_fields()
        fields.remove('ID')
        if not self.display_task_id(tid):
            return
        print("\nAvailable fields:")
        for ss, field in enumerate(self.humanize(fields),1):            
            print(f'{ss:02}.) {field}') 
        which = self.get_int("Field # to update: ")
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
        new_val = input(f"New value for {field}: ")
        if field == 'next_task':
            a_row = self.read_row_for_id(new_val)
            if a_row:
                new_val = a_row['uuid']
            else:
                new_val = 0
                print(f"Task #{new_val} not found. Set to Zero.")
                
        conn = sqlite3.connect(self.db_file)
        conn.execute(f"UPDATE todo SET {field} = ? WHERE ID = ?", (new_val, tid))
        conn.commit()
        conn.close()

    def mark_done(self):
        ''' Date task ID completed. '''
        self.show_task_numbers()
        tid = self.get_int("Enter Task ID to mark as done: ")
        if not tid:
            print("Aborted.")
            return
        row = self.read_row_for_id(tid)
        if not row:
            print(f"Task #{tid} not found.")
            return
        else:
            tid = row['uuid']            
        conn = sqlite3.connect(self.db_file)
        conn.execute("UPDATE todo SET date_done = ? WHERE uuid = ?",
                     (self.get_now(), tid))
        conn.commit()
        conn.close()

    def get_task_numbers(self)->list:
        ''' Return the ID's of all tasks. '''
        result = []
        query =  f"SELECT ID FROM todo ORDER BY ID"        
        conn = sqlite3.connect(self.db_file)
        rows = conn.execute(query).fetchall()
        for id_num in rows:
            result.append(id_num[0])
        conn.close()
        return result

    def show_task_numbers(self, wide=12)->None:
        ''' Display the ID's of all tasks. '''
        for ss, id_num in enumerate(self.get_task_numbers(), 1):
            if ss % wide == 0:
                print()
            print(f'#[{id_num:03}] ', end = '')
        print()

    def get_list_query(self, filter_type):
        query = f"SELECT * FROM todo"
        if filter_type == "pending":
            query += " WHERE date_done IS NULL OR date_done = ''"
        elif filter_type == "done":
            query += " WHERE date_done IS NOT NULL AND date_done != ''"        
        query += " ORDER BY project_name ASC, task_priority ASC"
        return query

    def list_tasks(self,filter_type="all")->int:
        ''' Returns the number of tasks shown. '''
        print(self.short_db_name())
        fields = self.get_fields()
        query = self.get_list_query(filter_type)
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query).fetchall()
        count = 0
        for r in rows:
            zrow = self.read_row_for_uuid(r['next_task'])
            if zrow:
                next_t = zrow['ID']
            else:
                next_t = 0
            count += 1
            self.display(r)
        conn.close()
        print(f"View [{filter_type.upper()}] is {count:03} of {self.count():03} items.")
        return count
    
    def list_pending(self):
        ''' List pending tasks. '''
        self.list_tasks("pending")

    def list_done(self):
        ''' List completed tasks. '''
        total = self.list_tasks("done")
        if total and total == self.count():
            message = "All DONE: You're a DoMaster!"
            stars = '*' * len(message)
            print(stars, message, stars, sep='\n')

    def list_all(self):
        ''' List all tasks. '''
        self.list_tasks("all")

    def project_report(self):
        ''' Show all project names. '''
        conn = sqlite3.connect(self.db_file)
        projs = conn.execute("SELECT DISTINCT project_name FROM todo ORDER BY project_name").fetchall()
        for p in projs: print(f"- {p[0]}")
        conn.close()

    def manage_files(self)->None:
        ''' Manage local files. '''
        ops = ManageFiles(self)
        ops.mainloop()


def mainloop():
    ops = DoMaster()
    options = {
        'Add Task':ops.add_task,
        'Delete Task':ops.delete_task,
        'Update Task':ops.update_task,
        'Mark Completed':ops.mark_done,
        'List Pendings':ops.list_pending,
        'List Done':ops.list_done,
        'List All':ops.list_all,
        'Projects':ops.project_report,
        'Swap Db':ops.swap_db,
        'File Manager':ops.manage_files,
        'Quit':ops.do_quit
        }
    Loop.MenuOps(ops, options, VERSION)

if __name__ == "__main__":
    mainloop()
