# MISSION: Provide a reusable menu / sub-menu framework.
# STATUS: Research
# VERSION: 1.0.0
# NOTES: Lighty tested. See the project for full documentation.
# DATE: 2026-02-21 10:32:43
# FILE: tui_loop.py
# AUTHOR: Randall Nagy
#

from ui_loop import *

class TuiLoop(MenuLoop):
    ''' Base class for all looping menu 'ops '''
    def __init__(self):
        ''' Prep menu instance for looping. '''
        super().__init__()

    def set_color(self, fore, back)->tuple:
        pass

    def input(self, *args, **kwargs):
        ''' Encapsulation for replacement. '''
        return input(*args)

    def print(self, *args, **kwargs):
        ''' Encapsulation for replacement. '''
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

    def is_done(self):
        ''' See if we're ready to exit. '''
        return self.b_done

    def do_app_exit(self):
        ''' Exit. '''
        # Exit management event. Plausable `destructor.`
        self.b_done = True

    def menu_ops(self, ops, options, title)->bool:
        ''' Re-usable API.is_done event with per-loop status reporting. '''
        line = '*' * len(title)
        API.do_print(title, line, sep='\n')
        keys = list(options.keys())
        times=0;errors=0;selection=None;entry=None
        while API.is_done() == False:
            API.loop_status(times=times, errors=errors,
                        selection=selection, entry=entry)
            for ss, op in enumerate(keys, 1):
                tag = f'{op}:'
                API.do_print(f'{ss:02}.) {tag:<18}{options[op].__doc__}')
            try:
                entry = selection = API.get_input("Enter #: ")
                which = int(selection.strip())
                times += 1; errors += 1
                if which > 0 and which <= len(keys):
                    times = 0
                    selection = keys[which-1]
                    if selection in options: # double check
                        API.do_print('*'*which, selection)
                        errors = 0           # RESET
                        options[selection]()
                else:
                    API.do_print(f"Invalid number {which}.")
            except ValueError:
                API.do_print("Numbers only, please.")
                continue
            except Exception as ex:
                API.do_print(ex)
                continue
        return True
