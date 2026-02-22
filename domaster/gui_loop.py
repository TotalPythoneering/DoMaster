# MISSION: Provide a reusable menu / sub-menu framework.
# STATUS: Research
# VERSION: 1.0.0
# NOTES: Lighty tested. See the project for full documentation.
# DATE: 2026-02-21 10:52:43
# FILE: gui_loop.py
# AUTHOR: Randall Nagy
#
from ui_loop import *
from gui_colors import COLORS
from gui_app import GuiApp

class GuiLoop(MenuDriver):
    ''' Base class for all GUI looping menu 'ops '''
    def __init__(self, ops, options, VERSION):
        ''' Prep menu instance for looping. '''
        super().__init__()
        self.fore = COLORS['yellow']
        self.back = COLORS['darkgreen']
        self.app = GuiApp(ops, options, VERSION)
        print("GUI detected.")

    def set_color(self, fore='yellow', back='darkgreen')->tuple:
        ''' Color means whatever print() makes of it.
        T/F and previous 'color' - if any - are always
        returned.
        '''
        ofore = self.fore; oback = self.back; br = False
        if fore in COLORS:
            self.fore = COLORS[fore]
            br = True
        if back in COLORS:
            self.back = COLORS[back]
            br = True
        return br, ofore, oback
    
    def do_quit(self):
        self.app.do_quit()

    def get_int(self, prompt, default=0):
        ''' Prompt to return an integral input, else the default value. '''
        return self.app.get_int(prompt, default)
        
    def input(self, *args, **kwargs):
        ''' Encapsulation for replacement. '''
        return self.app.get_input(*args, **kwargs)
        
    def print(self, *args, **kwargs):
        ''' Encapsulation for replacement. '''
        self.app.print(*args, **kwargs)
    
    def loop_status(self, **kwargs):
        pass

    def menu_ops(self, ops, options, menu_title):
        self.app.notify_menu_ops(ops, options, menu_title)

