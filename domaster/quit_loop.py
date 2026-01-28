# MISSION: Provide a reusable menu / sub-menu framework.
# STATUS: Research
# VERSION: 0.0.1
# NOTES: Worth a stand-alone sharing effort?
# DATE: 2026-01-28 05:20:30
# FILE: quit_loop.py
# AUTHOR: Randall Nagy
#

class Loop:
    ''' Base class for all looping menu 'ops '''
    def __init__(self):
        ''' Prep this loop for looping. '''
        self.b_done = False

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
        self.b_done = True
        
    @staticmethod
    def MenuOps(ops, options, title)->None:
        ''' Re-usable Menu 'Ops. '''
        line = '*' * len(title)
        print(title, line, sep='\n')
        keys = list(options.keys())
        times=0
        while ops.is_done() == False:
            ops.loop_status()
            for ss, op in enumerate(keys, 1):
                tag = f'{op}:'
                print(f'{ss:02}.) {tag:<18}{options[op].__doc__}')
            try:
                selection = input("Enter #: ")
                which = int(selection.strip())
                if which > 0 and which <= len(keys):
                    times = 0
                    selection = keys[which-1]
                    if selection in options: # double check
                        print('*'*which, selection)
                        options[selection]()
                else:
                    print(f"Invalid number {which}.")
            except Exception as ex:
                times += 1
                if times > 12:
                    print("I've no time for this - bye!")
                    ops.do_quit()
                print(ex)
                print("Numbers only, please.")
                continue


