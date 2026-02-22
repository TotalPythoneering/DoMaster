# MISSION: Maintain a set of global parameters witin any user's home-directory.
# STATUS: Research
# VERSION: 1.0.1
# NOTES: Testing Success - See the project for full documentation.
# DATE: 2026-02-07 09:07:21
# FILE: keeper.py
# AUTHOR: Randall Nagy
#
import os
import json
from pathlib import Path

OM_TYPE = '.json7'
OM_NAME = '.tp_keeper_keeps'

class Keeps:
    '''
Pure API class to manage object /
dictionary stowage within any user's
home directory. Options can either
be managed by tag, tag-value pair,
dictionary, any object's __ict__
set, or any combination of the same.
'''

    @staticmethod
    def name_file(file_name=None)->str:
        ''' Concoct a file name within this user's home folder.
Fully qualified paths will be 'homed into any user's same.
'''
        root = str(Path.home())
        if not file_name:
            return os.sep.join((root, (OM_NAME + OM_TYPE)))
        file_name = file_name.replace(OM_TYPE, '')
        if root not in file_name:
            return os.sep.join((root, (os.path.basename(file_name) + OM_TYPE)))
        return file_name

    @staticmethod
    def get_dict(file_name=None):
        """ Read data if it exists."""
        filepath = Keeps.name_file(file_name)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except:
                pass
        return None

    @staticmethod
    def put_dict(obj, file_name=None)->bool:
        if not isinstance(obj, dict):
            return False
        filepath = Keeps.name_file(file_name)
        try:
            with open(filepath, 'w') as f:
                json.dump(obj, f, indent=4)
            return os.path.exists(filepath)
        except IOError as e:
            pass
        return False

    @staticmethod
    def add_option(tag, value, file_name=None)->bool:
        '''
Add an option into the file-name.
Create option file if not found. '''
        data = Keeps.get_dict(file_name)
        if not data:
            data = dict()
        if tag:
            data[tag] = value
        return Keeps.put_dict(data, file_name)

    @staticmethod
    def del_option(tag, file_name=None)->bool:
        ''' Remove an option from the file_name. '''
        data = Keeps.get_dict(file_name)
        if not data:
            return False
        if tag and tag in data:
            del data[tag]
            return Keeps.put_dict(data, file_name)
        return True

    @staticmethod
    def get_option(tag, file_name=None, default_value=False)->bool:
        ''' Get an option from the file_name. '''
        data = Keeps.get_dict(file_name)
        if data and tag in data:
            return data[tag]
        return default_value

    @staticmethod
    def restore_obj(obj, file_name=None)->bool:
        """ Restore data if found + matches existing attribute."""
        data = Keeps.get_dict(file_name)
        if not data:
            return False
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return True
            
    @staticmethod
    def store_obj(obj, file_name=None)->bool:
        """ Persist data into home file. True on success. """
        if not hasattr(obj, '__dict__'):
            return False
        filepath = Keeps.name_file(file_name)
        if os.path.exists(filepath):
            os.unlink(filepath) # ctime
        if os.path.exists(filepath):
            return False        # yikes?
        if Keeps.put_dict(obj.__dict__):
            return os.path.exists(filepath)
        return False

# --- Test Cases ---
if __name__ == "__main__":
    import sys

    test_file = '~test'
    zname = Keeps.name_file(test_file)
    if os.path.exists(zname):
        os.unlink(zname)
    
    if not Keeps.add_option('foo', 'bar', test_file):
        print("Error 010: add_option failure")
        sys.exit(10)

    if not os.path.exists(zname):
        print("Error 020: add_option failure")
        sys.exit(20)

    if Keeps.get_option('foo', test_file) != 'bar':
        print("Error 030: get_option failure")
        sys.exit(30)

    if not Keeps.del_option('foo', test_file):
        print("Error 040: del_option failure")
        sys.exit(40)
        
    os.unlink(zname)
    if os.path.exists(zname):
        print("Error 090: add_option failure")
        sys.exit(90)
        
    class Obj:
        def __init__(self, name, age):
            self.name_file = name
            self.age  = age

    o1 = Obj('zoom',42)
    if not Keeps.store_obj(o1):
        print("Error 101: Unable to store_obj data.")
        sys.exit(101)

    o2 = Obj('',-1)    
    if not Keeps.restore_obj(o2):
        print("Error 102: Unable to restore_obj data.")
        sys.exit(102)

    if o2.name_file != o1.name_file or o2.age != o1.age:
        print("Error 103: restore_obj failure.")
        sys.exit(103)
        
    o1.name_file = None
    o1.age = None
    if not Keeps.store_obj(o1):
        print("Error 201: Unable to store_obj data.")
        sys.exit(201)

    if not Keeps.restore_obj(o2):
        print("Error 202: Unable to restore_obj data.")
        sys.exit(202)

    if o2.name_file != o1.name_file or o2.age != o1.age:
        print("Error 203: restore_obj failure.")
        sys.exit(203)

    zname = Keeps.name_file()
    print(f'Removing {zname}...')
    os.unlink(zname)
    if os.path.exists(zname):
        print("Error 900: Unable to remove file.")
        sys.exit(900)

    print("Testing Success!")
    sys.exit(0)
