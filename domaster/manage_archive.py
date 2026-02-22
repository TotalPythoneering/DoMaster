# MISSION: Manage AUTOMATIC ARCHIVAL options.
# STATUS: Research
# VERSION: 1.0.0
# NOTES: GLOBAL database needs to be backed-up. Even auto.
# ManageArchived keeps the location + data for ARCHIVAL 'self.
# DATE: 2026-02-21 10:54:08
# FILE: manage_archive.py
# AUTHOR: Randall Nagy
#
import os, sys, shutil
import sqlite3
import uuid
import csv
import datetime

if '..' not in sys.path:
    sys.path.insert(0, '..')
from ui_loop import API, MenuLoop
from domaster.sync_tool import SQLiteCSVSync
from domaster.keeper import Keeps

class ManageArchived(MenuLoop):
    ''' Single archive to sync same into any archival sweep-path. '''
    def __init__(self, mega):
        super().__init__()
        self.mega = mega

    def assign_archive(self):
        ''' Set archive location. '''
        folder = Keeps.get_option('backup', default_value="unspecified")
        API.do_print(f'Archive folder is [{folder}].')
        folder = API.get_input("Backup folder: ").strip()
        if not folder:
            yn = API.get_input("Clear archive option? y/n ").lower()
            if yn[0] != 'y':
                API.do_print("Aborted.")
                return False
        if not os.path.exists(folder):
            API.do_print(f"Folder [{folder}] not found.")
        else:
            if not Keeps.add_option('backup', folder):
                API.do_print(f"Error. Unable to set [{folder}]")
            else:
                API.do_print(f"Backup folder is now [{folder}]")
                return True
        return False

    def _is_ok(self, yikes)->bool:
        if os.path.exists(yikes):
            yn = API.get_input(f"Ok to replace {yikes}? y/n ").lower()
            return yn[0] == 'y'
        return True

    def safe_clone(self, source, archive)->True:
        source = source.replace(r'\\','/')
        archive= archive.replace(r'\\','/')
        if not os.path.exists(source):
            API.do_print(f"Error: Unable to stat [{source}].")
            return False
        if self.is_ok(archive):
            if os.path.exists(archive):
                os.unlink(archive)
                if os.path.exists(archive):
                    API.do_print(f"Error: Unable to delete [{archive}].")
                    return False
            shutil.copyfile(source, archive)
            if not os.path.exists(archive):
                API.do_print(f"Error: Unable to create [{archive}].")
                return False
            API.do_print(f"Success: Created [{archive}].")
            return True

    def create_archive(self)->bool:
        ''' Create database archive. '''
        folder = Keeps.get_option('backup')
        if not folder:
            API.do_print("Error: Please select backup location.")
            return False        
        archive = os.sep.join((folder, 'archive.db'))
        return self.safe_clone(self.mega.db_file, archive)

    def restore_archive(self):
        ''' Restore database archive. '''
        folder = Keeps.get_option('backup')
        if not folder:
            API.do_print("Please select backup location.")
            return False        
        archive = os.sep.join((folder, 'archive.db'))
        return self.safe_clone(archive, self.mega.db_file)

    def auto_archive(self):
        ''' Toggle automatic archive. '''
        auto = br = Keeps.get_option('auto_backup')
        if br:
            br = Keeps.add_option('auto_backup', False)
            auto = False
        else:
            br = Keeps.add_option('auto_backup', True)
            auto = True
        if not br:
            API.do_print("Error: Unable to toggle database auto.")
            return
        stat = "On" if auto else "Off"
        API.do_print(f"Automatic database backup is now [{stat}]")
    
    def mainloop(self)->None:
        if not self.mega.is_global:
            API.do_print("Archival is for global database, only.")
            return
        options = {
            'Archive Folder':self.assign_archive,
            'Create Archive':self.create_archive,
            'Restore Archive':self.restore_archive,
            'Auto Archive':self.auto_archive,
            'Quit':self.do_quit
            }
        folder = Keeps.get_option('backup', default_value="unspecified")
        API.do_print(f'Archive folder is [{folder}].')
        API.menu_ops(self, options, "Archive Manager")


if __name__== '__main__':
    API.init()
    from domaster.main import DoMaster 
    sut = ManageArchived(DoMaster())
    sut.mainloop()
