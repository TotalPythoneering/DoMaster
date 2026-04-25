# MISSION: Start the TK interface to the GLOBAL database.
# STATUS: Production
# VERSION: 1.0.0
# NOTES: New
# DATE: 2026-04-25 06:42:40
# FILE: tkdo.py
# AUTHOR: Randall Nagy
#

import sys
if '..' not in sys.path:
    sys.path.insert(0, '..')

def mainloop():
    import tkinter as tk
    from . TkDomaster import TodoApp
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()


if __name__== "__main__":
    mainloop()
