# MISSION: Manage AUTOMATIC ARCHIVAL options.
# STATUS: Research
# VERSION: 0.0.3
# NOTES: GLOBAL database needs to be backed-up. Even auto.
# ManageArchived keeps the location + data for ARCHIVAL 'ops.
# DATE: 2026-02-08 10:34:35
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
from domaster.tui_loop import Loop
from domaster.sync_tool import SQLiteCSVSync
from domaster.keeper import Keeps

class ManageArchived(Loop):
    ''' Single archive to sync same into any archival sweep-path. '''
    def __init__(self, mega):
        super().__init__()
        self.mega = mega

    def assign_archive(self):
        ''' Set archive location. '''
        folder = Keeps.get_option('backup', default_value="unspecified")
        self.print(f'Archive folder is [{folder}].')
        folder = self.input("Backup folder: ").strip()
        if not folder:
            yn = self.input("Clear archive option? y/n ").lower()
            if yn[0] != 'y':
                self.print("Aborted.")
                return False
        if not os.path.exists(folder):
            self.print(f"Folder [{folder}] not found.")
        else:
            if not Keeps.add_option('backup', folder):
                self.print(f"Error. Unable to set [{folder}]")
            else:
                self.print(f"Backup folder is now [{folder}]")
                return True
        return False

    def _is_ok(self, yikes)->bool:
        if os.path.exists(yikes):
            yn = self.input(f"Ok to replace {yikes}? y/n ").lower()
            return yn[0] == 'y'
        return True

    def safe_clone(self, source, archive)->True:
        source = source.replace(r'\\','/')
        archive= archive.replace(r'\\','/')
        if not os.path.exists(source):
            self.print(f"Error: Unable to stat [{source}].")
            return False
        if self._is_ok(archive):
            if os.path.exists(archive):
                os.unlink(archive)
                if os.path.exists(archive):
                    self.print(f"Error: Unable to delete [{archive}].")
                    return False
            shutil.copyfile(source, archive)
            if not os.path.exists(archive):
                self.print(f"Error: Unable to create [{archive}].")
                return False
            self.print(f"Success: Created [{archive}].")
            return True

    def create_archive(self)->bool:
        ''' Create database archive. '''
        folder = Keeps.get_option('backup')
        if not folder:
            self.print("Error: Please select backup location.")
            return False        
        archive = os.sep.join((folder, 'archive.db'))
        return self.safe_clone(self.mega.db_file, archive)

    def restore_archive(self):
        ''' Restore database archive. '''
        folder = Keeps.get_option('backup')
        if not folder:
            self.print("Please select backup location.")
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
            self.print("Error: Unable to toggle database auto.")
            return
        stat = "On" if auto else "Off"
        self.print(f"Automatic database backup is now [{stat}]")
    
    def mainloop(ops)->None:
        if not ops.mega.is_global:
            self.print("Archival is for global database, only.")
            return
        options = {
            'Archive Folder':ops.assign_archive,
            'Create Archive':ops.create_archive,
            'Restore Archive':ops.restore_archive,
            'Auto Archive':ops.auto_archive,
            'Quit':ops.do_quit
            }
        folder = Keeps.get_option('backup', default_value="unspecified")
        ops.print(f'Archive folder is [{folder}].')
        Loop.MenuOps(ops, options, "Archive Manager")


if __name__ == '__main__':
    from domaster.main import DoMaster 
    sut = ManageArchived(DoMaster())
    sut.mainloop()
