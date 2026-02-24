# MISSION: Provide a reusable menu / sub-menu framework.
# STATUS: Research
# VERSION: 1.0.0
# NOTES: Lighty tested. See the project for full documentation.
# DATE: 2026-02-21 10:32:43
# FILE: tui_loop.py
# AUTHOR: Randall Nagy
#
import sys
if '..' not in sys.path:
    sys.path.insert(0, '..')
    
from domaster.ui_loop import *

class TuiLoop(MenuDriver):
    ''' Base class for all looping menu 'ops '''
    def __init__(self):
        ''' Prep menu instance for looping. '''
        super().__init__()
        self.ops = None
        self.options = None
        self.title = None
        self.ops_stack = []

    def set_color(self, fore, back)->tuple:
        pass

    def input(self, *args, **kwargs):
        ''' Encapsulation for replacement. '''
        return input(*args)

    def print(self, *args, **kwargs):
        ''' Encapsulation for replacement. '''
        if len(args):
            for ss in range(len(args)):
                for rm in API.CALT, API.CERR:
                    args[ss] = args[ss].replace(rm, '')
        print(*args, **kwargs)

    def loop_status(self, **kwargs):
        ''' Operational state before each loop.
        kwargs['times']     = times through loop
        kwargs['errors']    = errors since last success
        kwargs['selection'] = raw user input string
        kwargs['entry']     = last completed event name
        '''
        pass

    def get_int(self, prompt, default=0):
        ''' Prompt to return an integral input, else the default value. '''
        result = default
        try:
            result = int(self.input(prompt))
        except:
            pass
        return result

    def show_dict(self, ops, a_dict:dict, title:str)->bool:
        return super().show_dict(ops, a_dict, title)

    def get_dict(self, ops, a_dict:dict, title:str):#->tuple[bool, str]:
        return super().get_dict(ops, a_dict, title)

    def do_quit(self):
        if not self.ops_stack:
            super().do_quit()
        else:
            frame = self.ops_stack.pop()
            self.ops = frame[0]
            self.options = frame[1]
            self.title = frame[2]
            self.show_menu()

    def menu_ops(self, ops, options, title)->bool:
        ''' Stackable menu logic. '''
        if self.ops:
            self.ops_stack.append([self.ops, self.options, self.title])
        self.ops = ops; self.options = options; self.title = title
        self.show_menu()

    def show_menu(self):
        ''' Support reveal and redraw requirements '''
        line = '*' * len(self.title)
        self.print(self.title, line, sep='\n')
        keys = list(self.options.keys())
        times=0;errors=0;selection=None;entry=None
        while self.is_done() == False:
            self.loop_status(times=times, errors=errors,
                        selection=selection, entry=entry)
            for ss, op in enumerate(keys, 1):
                tag = f'{op}:'
                self.print(f'{ss:02}.) {tag:<18}{self.options[op].__doc__}')
            try:
                entry = selection = self.input("Enter #: ")
                which = int(selection.strip())
                times += 1; errors += 1
                if which > 0 and which <= len(keys):
                    times = 0
                    selection = keys[which-1]
                    if selection in self.options: # double check
                        self.print('*'*which, selection)
                        errors = 0           # RESET
                        self.options[selection]()
                else:
                    self.print(f"Invalid number {which}.")
            except ValueError:
                self.print("Numbers only, please.")
                continue
            except Exception as ex:
                self.print(ex)
                continue
        return True
