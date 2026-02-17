# MISSION: Provide a reusable menu / sub-menu framework.
# STATUS: Research
# VERSION: 0.0.0

from tui_loop import Loop
from gui_colors import COLORS

class GuiLoop(Loop):
    ''' Base class for all looping menu 'ops '''
    def __init__(self):
        ''' Prep menu instance for looping. '''
        super().__init__(self)

    def set_color(self, color)->tuple:
        ''' Color means whatever print() makes of it.
        T/F and previous 'color' - if any - are always
        returned.
        '''
        result = self.color
        self.color = color
        return True, result

    def print(self, *args, **kwargs):
        ''' Encapsulation for replacement. '''
        print(*args, **kwargs)

