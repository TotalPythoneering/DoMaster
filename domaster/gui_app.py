# MISSION: Create a reusable GUITUI Framework.
# STATUS: Research
# VERSION: 2.0.1
# NOTES: Works well.
# DATE: 2026-02-24 04:48:58
# FILE: gui_app.py
# AUTHOR: Randall Nagy
#
import sys
import tkinter as tk

if '..' not in sys.path:
    sys.path.insert(0, '..')
from domaster.ui_loop import API

class GuiApp(tk.Tk):
    """
    The GUI part of the GuiTui mission.
    """    
    def __init__(self, ops, options, version_title):
        super().__init__()

        # menu loop information:
        self.is_app_done= False
        self.ops_stack  = []
        self.ops        = ops
        self.options    = options
        self.menu_title = version_title
        self.content    = None
        
        # status loop information:
        self.utimes    = 0
        self.uerrors   = 0
        self.uselection= None
        self.uentry    = None
        
        # tkwindow configuration:
        self.title(self.menu_title)
        self._maximize_window()
        self.configure(bg="forest green")
        
        # application styles and constants:
        self.app_font = ("Courier", 18)
        self.bg_color = "forest green"
        self.fg_color = "yellow"

        # application setup & initialization:
        self.button_pressed = tk.IntVar(value=0)
        self._setup_widgets()
        self._bind_events()
        self.submit_btn.after(1000, self.show_menu())

    def _maximize_window(self):
        """Cross-platform method to fill the screen."""
        if sys.platform.startswith('win'):
            # Windows
            self.state('zoomed')
        elif sys.platform.startswith('linux'):
            # Linux (X11)
            self.attributes('-zoomed', True)
        else:
            # macOS and others: use full-screen attribute
            self.attributes('-fullscreen', True)

    def _setup_widgets(self):
        """Initializes and layouts all GUI components."""
        # Top Display Area (Text View)
        self.display_frame = tk.Frame(self, bg=self.bg_color)
        self.display_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.text_display = tk.Text(
            self.display_frame, 
            bg=self.bg_color, 
            fg=self.fg_color, 
            font=self.app_font,
            highlightthickness=0,
            border=0
        )
        self.text_display.pack(expand=True, fill="both")
        
        # Result Tag: Specifically set output text to red [Original Request]
        self.text_display.tag_config("default_text", foreground="yellow")
        self.text_display.tag_config("hi_text", foreground="white")
        self.text_display.tag_config("user_text", foreground="aqua")
        self.text_display.tag_config("error_text", foreground="red")
        
        # Bottom Input Area
        self.input_frame = tk.Frame(self, bg=self.bg_color)
        self.input_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        # Submit Button (Placed to the LEFT of the input)
        self.submit_btn = tk.Button(
            self.input_frame, 
            text="Submit", 
            command=self.tui_input,
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.app_font,
            padx=15
        )
        self.submit_btn.pack(side="left", padx=(0, 20))

        # Entry Field (Input Edit)
        self.entry = tk.Entry(
            self.input_frame, 
            bg=self.bg_color, 
            fg=self.fg_color, 
            insertbackground=self.fg_color,  # Cursor color
            font=self.app_font,
            border=2
        )
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.focus_set()

    def do_destroy(self):
        self.destroy()

    def _bind_events(self):
        """Binds keyboard events."""
        self.bind('<Return>', self.tui_input)  # Enter key support
        self.bind('<Escape>', self.do_destroy)  # Easy exit for full screen

    def get_dlg_int(self, prompt, default=0)->int:
        ''' Prompt to return an integral input, else the default value. '''
        from domaster.gui_edit import Edit
        dlg = Edit(self, 'DoMaster', prompt, int)
        result = dlg.result
        if not result:
            result = default
        dlg.destroy()
        return result

    def get_dlg_input(self, prompt, default='')->str:
        ''' Prompt to return an integral input, else the default value. '''
        from domaster.gui_edit import Edit
        dlg = Edit(self, 'DoMaster', prompt, str)
        result = dlg.result
        if not result:
            result = default
        dlg.destroy()
        return result

    def get_int(self, prompt, default=0)->int:
        ''' Prompt to return an integral input, else the default value. '''
        self.print(prompt, sep='', tag='hi_text')
        self.button_pressed.set(9000)
        self.submit_btn.wait_variable(self.button_pressed)
        self.button_pressed.set(0)
        if not self.content:
            return default
        return self.content

    def get_input(self, prompt, default='')->str:
        ''' Prompt to return an integral input, else the default value. '''
        self.print(prompt, sep='', tag='hi_text')
        self.button_pressed.set(9000)
        self.submit_btn.wait_variable(self.button_pressed)
        self.button_pressed.set(0)
        if not self.content:
            return default
        return self.content
    
    def tui_input(self, *args, **kwargs):
        """Retrieves input, prints the results, and clears entry."""
        self.content = self.entry.get()
        self.print(self.content, tag='user_text')
        self.entry.delete(0, tk.END)
        if self.button_pressed.get() == 9000:
            self.button_pressed.set(1)
            return
        try:
            which = int(self.content.strip())
            self.utimes += 1; self.uerrors += 1
            keys = list(self.options.keys())
            if which > 0 and which <= len(keys):
                self.utimes = 0
                selection = keys[which-1]
                if selection in self.options: # double check
                    self.uerrors = 0          # RESET
                    self.options[selection]()
                else:
                    self.show_menu()
                return
            else:
                self.print(f"Invalid number {which}.")
        except ValueError:
            self.print("Numbers only, please.")

    def do_quit(self):
        self.pop_ops()

    def print(self, *args, **kwargs):
        # Add text with the 'default_text' tag
        lines = API.parse_ccodes(args)
        sep = '\n'
        if 'sep' in kwargs:
            sep = kwargs['sep']
        tag =  "default_text"
        if 'tag' in kwargs:
            tag = kwargs['tag']
        for line in lines:
            for value in line:
                if value[0] == API.CERR:
                    tag = 'error_text'
                elif value[0] == API.CALT:
                    tag = 'hi_text'
                self.text_display.insert(
                    tk.END, f"{value[1]}", tag)
            self.text_display.insert(
                tk.END, f"{sep}", tag)
        self.text_display.see(tk.END)  # Auto-scroll

    def push_ops(self):
        self.ops_stack.append([self.ops, self.options, self.menu_title])

    def pop_ops(self): 
        if not self.ops_stack:
            # We're done!
            self.is_app_done = True
            self.destroy()
        else:
            # Show previous menu options:
            frame = self.ops_stack.pop()
            self.ops = frame[0]
            self.options = frame[1]
            self.menu_title = frame[2]
            self.show_menu()

    def notify_menu_ops(self, ops, options, menu_title)->bool:
        ''' Update the information for the main loop. '''
        self.push_ops()
        self.ops = ops
        self.options = options
        self.menu_title = menu_title
        self.show_menu()
        return True
    
    def show_menu(self):
        if self.is_app_done:
            return
        seg = '~' * len(self.menu_title)
        line = '\n' + seg
        self.print(self.menu_title, line, sep='\n')
        keys = list(self.options.keys())
        times=0;errors=0;selection=None;entry=None
##          API.loop_status(times=times, errors=errors,
##              selection=selection, entry=entry)
        for ss, op in enumerate(keys, 1):
            tag = f'{op}:'
            self.print(f'{ss:02}.) {tag:<18}{self.options[op].__doc__}')


