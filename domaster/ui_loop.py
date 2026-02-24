# MISSION: Manage a to-do list or / and ideas.
# STATUS: Testing
# VERSION: 1.0.0
# NOTES: Lighty tested. See the project for full documentation.
# DATE: 2026-02-21 10:40:11
# FILE: ui_loop.py
# AUTHOR: Randall Nagy
#
import sys
if '..' not in sys.path:
    sys.path.insert(0, '..')

class API:
    ui_driver = None
    is_gui = False
    CNONE = '✌' # Default text color.
    CALT  = '👍' # Start & end ALT color
    CERR  = '😲' # Start & end ERROR color
    
    @staticmethod
    def init():
        ''' Set up the TUI '''
        if API.ui_driver: return
        from tui_loop import TuiLoop
        API.ui_driver = TuiLoop()
        is_gui = False

    def parse_ccodes(*args):#->list[list[str, str]]
        ''' Parse string[s] into colorizable lines & line segments. '''
        lines = []
        for tup in args:
            seg = ''; line = []; esc = API.CNONE
            for arg in tup:
                for ch in str(arg):
                    found = False
                    for comp in API.CERR, API.CALT, API.CNONE:
                        if ch == comp:
                            found = True
                            if seg:
                                line.append([esc, seg])
                                seg = ''
                            esc = comp
                            break
                    if not found:
                        seg += ch
                if seg:
                    line.append([esc, seg])
                if not line:
                    line.append([API.CNONE, arg])
            lines.append(line)
        return lines

    @staticmethod
    def set_gui(ops, options, VERSION):
        ''' Try to set up the GUI - False if using TUI '''
        from domaster.tui_loop import TuiLoop
        from domaster.gui_loop import GuiLoop
        try:
            # int('boom')
            API.ui_driver = GuiLoop(ops, options, VERSION)
            API.is_gui = True
            return True
        except Exception as ex:
            print(ex)
            API.init()
            return False
        
    @staticmethod
    def set_color(fore, back)->tuple:
        API.ui_driver.set_color(fore, back)

    @staticmethod
    def get_input(*args, **kwargs):
        return API.ui_driver.input(*args, **kwargs)

    @staticmethod
    def do_print(*args, **kwargs):
        API.ui_driver.print(*args, **kwargs)

    @staticmethod
    def loop_status(**kwargs):
        API.ui_driver.loop_status(**kwargs)

    @staticmethod
    def get_int(prompt, default=0)->int:
        return API.ui_driver.get_int(prompt, default)
    
    @staticmethod
    def show_dict(ops, a_dict:dict, title:str): #->tuple[bool, str]
        return API.ui_driver.show_dict(ops, a_dict, title)
    
    @staticmethod
    def get_dict(ops, a_dict:dict, title:str): #->tuple[bool, str]
        return API.ui_driver.get_dict(ops, a_dict, title)

    @staticmethod
    def is_done():
        return API.ui_driver.is_done()

    @staticmethod
    def do_quit():
        ''' Exit '''
        API.ui_driver.do_quit()

    @staticmethod
    def menu_ops(ops, options, title)->bool:
        return API.ui_driver.menu_ops(ops, options, title)


class MenuLoop:
    ''' Support common API.menu_ops(above) ''' 
    def __init__(self):
        self._b_done = False

    def is_done(self):
        return self._b_done

    def reset(self):
        self._b_done = False


from abc import ABC, abstractmethod
class MenuDriver(MenuLoop, ABC):

    @abstractmethod
    def set_color(self, fore, back)->tuple:
        pass

    @abstractmethod
    def input(self, *args, **kwargs):
        pass

    @abstractmethod
    def print(self, *args, **kwargs):
        pass

    @abstractmethod
    def loop_status(self, **kwargs):
        pass

    @abstractmethod
    def get_int(self, prompt, default=0)->int:
        pass

    @abstractmethod
    def show_dict(self, ops, a_dict:dict, title:str)->bool:
        if not ops or not a_dict:
            return False, "Error: Bad input data."
        for ss, key in enumerate(a_dict, 1):
            API.print(f"{ss:02}.) {key} [{a_dict[key]}]")
        return True, "Success."

    @abstractmethod
    def get_dict(self, ops, a_dict:dict, title:str)->tuple[bool, str]:
        while True:
            result = API.show_dict(ops, a_dict, title)
            if not result[0]:
                return result
            which = API.get_int("Which # to edit? ")
            if not which:
                return False, "User exit."
            which = which - 1
            if which < 0 or which > len(a_dict):
                API.print(f"Bad field number.")
                continue
            items = a_dict.get_items()
            API.print(f"{items[0]}: [{items[1]}]")
            value = API.get_input(f"Update {items[0]}: ")
            if not value:
                API.print("Aborted.")
                return False, "User exit."
            a_dict[items[0]] = value
            # TODO: Untested.

    @abstractmethod
    def do_quit(self):
        self._b_done = True

    @abstractmethod
    def menu_ops(self, ops, options, title)->bool:
        pass


if __name__ == '__main__':
    for line in API.parse_ccodes(f'one{API.CALT}TWO{API.CALT}three'):
        print(line)

    for line in API.parse_ccodes(f'one{API.CERR}TWO{API.CERR}three'):
        print(line)

    for line in API.parse_ccodes(f'one{API.CNONE}TWO{API.CNONE}three'):
        print(line)

