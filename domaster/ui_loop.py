# MISSION: Manage a to-do list or / and ideas.
# STATUS: Testing
# VERSION: 1.0.0
# NOTES: Lighty tested. See the project for full documentation.
# DATE: 2026-02-21 10:40:11
# FILE: ui_loop.py
# AUTHOR: Randall Nagy
#
class API:
    ui_driver = None
    is_gui = False
    
    @staticmethod
    def init():
        ''' Set up the TUI '''
        if API.ui_driver: return
        from tui_loop import TuiLoop
        API.ui_driver = TuiLoop()
        is_gui = False

    @staticmethod
    def set_gui(ops, options, VERSION):
        ''' Try to set up the GUI - False if using TUI '''
        from tui_loop import TuiLoop
        from gui_loop import GuiLoop
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
    def set_color(fore, back)->tuple:
        pass

    @abstractmethod
    def input(*args, **kwargs):
        pass

    @abstractmethod
    def print(*args, **kwargs):
        pass

    @abstractmethod
    def loop_status(**kwargs):
        pass

    @abstractmethod
    def get_int(prompt, default=0)->int:
        pass

    @abstractmethod
    def do_quit(self):
        self._b_done = True

    @abstractmethod
    def menu_ops(ops, options, title)->bool:
        pass


