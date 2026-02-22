# MISSION: Manage HTML reports, backups, and exported data files.
# STATUS: Production
# VERSION: 2.0.0
# NOTES: Works well.
# DATE: 2026-02-21 10:37:12
# FILE: manage_files.py
# AUTHOR: Randall Nagy
#
import os, sys, shutil
import sqlite3
import uuid
import csv
import datetime

if '..' not in sys.path:
    sys.path.insert(0,'..')
from ui_loop import API, MenuLoop
from domaster.sync_tool import SQLiteCSVSync
from domaster.keeper import Keeps

class ManageFiles(MenuLoop):

    def __init__(self, db):
        super().__init__()
        self.db = db

    def archive_options(self):
        ''' Database archival options. '''
        from domaster.manage_archive import ManageArchived
        return ManageArchived(self.db).mainloop()


    def export_html_file(self, filename, status="pending")->int:
        # TODO: Add CSS (et al.)
        ''' Generate the HTML report into file. Returns number exported. '''
        if self.db.count() == 0:
            API.do_print("Database is empty.")
            return 0
        conn = sqlite3.connect(self.db.db_file)
        conn.row_factory = sqlite3.Row
        query = self.db.get_list_query(status)
        rows = conn.execute(query).fetchall()
        if  status == "pending":
            group_field = 'project_name'
        else:
            group_field = 'date_done'
        count = 0
        with open(filename, "w") as f:
            f.write(f"<html><body><h1>DoMaster [{status.upper()}] Report</h1>")
            current_group = None
            for r in rows:
                if r[group_field] != current_group:
                    current_group = r[group_field]
                    f.write(f"<h2>{current_group}</h2>")
                f.write('<hr>')
                count += 1
                adict = dict(r)
                del adict['uuid']
                for tag in adict:
                    value = adict[tag]
                    if tag == 'next_task':
                        post = self.db.read_row_for_uuid(value)
                        if post:
                            value = post['ID']
                    htag = self.db.humanize(tag)
                    f.write(f"<b>{htag}:</b>&nbsp;&nbsp;{value}<br>")
        API.do_print(f"Report exported to {filename}")
        conn.close()
        return count

    def export_html(self, status="pending")->int:
        ''' Name + generate the HTML report. Returns number exported. '''
        source = 'global' if self.db.is_db_global() else 'local'
        filename = f"{source}_report_{status}_{datetime.date.today()}.html"
        return self.export_html_file(filename, status)

    def html_report(self):
        ''' Create the HTML Report. '''
        if self.db.count() == 0:
            API.do_print("Database is empty.")
            return
        total_pending = self.export_html("pending")
        total_done    = self.export_html("done")
        if total_pending == total_done == 0:
            API.do_print("No items exported.")
        else:
            API.do_print(f'Pending: {total_pending:03}, Done: {total_done:03}')

    def export_csv(self, dated=False, folder=None)->bool:
        ''' Export to CSV file. '''
        if self.db.count() == 0:
            API.do_print("Database is empty.")
            return False
        mgr = SQLiteCSVSync(self.db.db_file, 'todo', self)
        zfile = 'domaster.csv'
        safe = self.db.get_now().replace(':','-').replace(' ','@')
        if os.path.exists(zfile):
            ztmp = '~' + safe + '_' + zfile
            shutil.copyfile(zfile, ztmp)
            API.do_print(f'Saved older {zfile} as {ztmp}.')
        if dated:
            zfile =  f'~domaster_backup_{safe}.csv'
        if folder:
            # DEFER TO USER-SPECIFIED ARCHIVE PATH
            if not os.path.exists(folder):
                API.do_print(f"Folder [{folder}] not found.")
                return False
            zfile = os.sep.join((folder, zfile))
        num = mgr.export_to_csv(zfile)
        if num == -1:
            API.do_print('Aborted.')
            return False # error abort
        br = True
        if not num:
            API.do_print(f"Error: Unable to export {zfile} file.")
            br = False
        else:
            API.do_print(f"Success: Exported {zfile}.")
        return br

    def import_csv(self, file_name=None)->bool:
        ''' Import CSV file into the database. '''
        mgr = SQLiteCSVSync(self.db.db_file, 'todo', self)
        zfile = 'domaster.csv'
        if file_name:
            zfile = file_name
        br = mgr.import_from_csv(zfile)
        if not br:
            API.do_print(f"Error: Unable to import {zfile} file.")
        else:
            API.do_print(f"Success: Imported {zfile}.")
        return br

    def backup_and_empty(self)->None:
        ''' Export & reset TODO list. '''
        if self.db.count() == 0:
            API.do_print("Database is empty.")
            return
        cando = API.get_input("Okay to blank the database? ").strip().lower()
        if not cando or cando[0] != 'y':
            API.do_print("Aborted.")
            return
        folder = Keeps.get_option("backup", default_value=None)
        if folder:
            yn = API.get_input(f"Export to [{folder}]? y/n ").strip().lower()
            if yn and yn[0] != 'y':
                folder = None
        if not self.export_csv(True, folder=folder):
            return
        conn = sqlite3.connect(self.db.db_file)
        try:
            conn.execute("DELETE FROM todo WHERE ID IS NOT 0;")
            conn.commit()
            API.do_print("Success: All tasks removed.")
        except Exception as ex:
            API.do_print(f"Error: Unable to reset {self.db.db_file}.")
        finally:
            conn.close()

    def get_artis(self)->list:
        ''' List the arifacts, if any. '''
        files = []
        for file in os.listdir():
            c_file = str(file) # remove embedded quotes
            if c_file.endswith('.csv') or c_file.endswith('.html'):
                files.append(c_file)
        return files

    def copy_data(self)->None:
        ''' Copy exported artifacts. '''
        files = self.get_artis()
        if not files:
            API.do_print('No files.')
            return
        for ss, file in enumerate(files, 1):
            API.do_print(f'{ss}.) {file}')
        try:
            which = API.get_int('Copy #: ')
            if not which:
                API.do_print("Aborted.")
                return
            which -= 1
            ofile = files[which]
            nfile = API.get_input(f'Copy {ofile} to: ').strip()
            if not nfile:
                API.do_print("Aborted.")
                return
            if os.path.exists(nfile):
                API.do_print(f'File {nfile} already exists.')
                API.do_print('Please use another file name.')
            else:
                shutil.copyfile(ofile, nfile)
                if os.path.exists(nfile):
                    API.do_print(f'Copied {ofile} to {nfile}.')
                else:
                    API.do_print(f'Error: Unable to create {nfile}.')
        except:
            API.do_print(f"Invalid entry.")

    def remove_temp_files(self)->None:
        ''' Remove exported artifacts. '''
        files = self.get_artis()
        if not files:
            API.do_print('No temporary files to remove.')
            return
        for file in files:
            API.do_print(f'* {file}')
        dum = API.get_input('Remove these files? y/n ').lower()
        if not dum or dum[0] != 'y':
            API.do_print('Aborted.')
            return
        for file in files:
            os.unlink(file)
            if os.path.exists(file):
                API.do_print(f"Warning: Unable to remove {file}.")
            else:
                API.do_print(f"Removed {file}.")
                    
    def mainloop(self)->None:
        options = {
            'HTML Report':self.html_report,
            'Archive':self.archive_options,
            'Export Data':self.export_csv,
            'Import Data':self.import_csv,
            'Reset Database':self.backup_and_empty,
            'Copy Data':self.copy_data,
            'Cleanup':self.remove_temp_files,
            'Quit':API.do_quit
            }
        API.menu_ops(self, options, "File Manager")


if __name__ == '__main__':
    API.init()
    from domaster.main import DoMaster
    sut = ManageFiles(DoMaster())
    sut.mainloop()
