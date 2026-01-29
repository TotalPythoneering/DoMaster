# MISSION: Provide a reusable menu / sub-menu framework.
# STATUS: Research
# VERSION: 0.1.0
# NOTES: Support quitable TUI 'ops. Features:
#       💡 Event: loop_status(...)
#           ✓ Operational state before each loop.
#             ☑ Total times through loop.
#             ☑ Raw user input string.
#             ☑ Last completed event name.
#             ☑ Errors since last success.
#       💡 Event: do_quit()
#           ✓ Supports plausable 'app `destructor.`
# DATE: 2026-01-29 05:39:18
# FILE: tui_loop.py
# AUTHOR: Randall Nagy
#
class Loop:
    ''' Base class for all looping menu 'ops '''
    def __init__(self):
        ''' Prep menu instance for looping. '''
        self.b_done = False

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
            result = int(input(prompt))
        except:
            pass
        return result

    def is_done(self):
        ''' See if we're ready to exit. '''
        return self.b_done

    def do_quit(self):
        ''' Exit. '''
        # Exit management event. Plausable `destructor.`
        self.b_done = True
        
    @staticmethod
    def MenuOps(ops, options, title)->bool:
        ''' Re-usable is_done event with per-loop status reporting. '''
        if not isinstance(ops, Loop):
            print('Error: Please inherit from Loop.')
            return False
        line = '*' * len(title)
        print(title, line, sep='\n')
        keys = list(options.keys())
        times=0;errors=0;selection=None;entry=None
        while ops.is_done() == False:
            ops.loop_status(times=times, errors=errors,
                            selection=selection, entry=entry)
            for ss, op in enumerate(keys, 1):
                tag = f'{op}:'
                print(f'{ss:02}.) {tag:<18}{options[op].__doc__}')
            try:
                entry = selection = input("Enter #: ")
                which = int(selection.strip())
                times += 1; errors += 1
                if which > 0 and which <= len(keys):
                    times = 0
                    selection = keys[which-1]
                    if selection in options: # double check
                        print('*'*which, selection)
                        errors = 0           # RESET
                        options[selection]()
                else:
                    print(f"Invalid number {which}.")
            except Exception as ex:
                print(ex)
                print("Numbers only, please.")
                continue
        return True
