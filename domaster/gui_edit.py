# MISSION: Create a reusable GUITUI Framework.
# STATUS: Research
# VERSION: 0.0.1
# NOTES: GUI default.
# DATE: 2026-02-21 02:30:19
# FILE: gui_edit.py
# AUTHOR: Randall Nagy
#
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime

import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime

class Edit(simpledialog.Dialog):
    def __init__(self, parent, title, prompt, dtype=str):
        self.prompt = prompt
        self.dtype = dtype
        self.font = ("Courier", 18)
        super().__init__(parent, title)

    def body(self, master):       
        # Styled Label
        tk.Label(master, text=self.prompt,
                 font=self.font).grid(row=0, padx=20, pady=20)
        
        # Styled Edit Box (Entry)
        # bg: box background | fg: typed text color | insertbackground: cursor color
        self.entry = tk.Entry(master, 
                              font=self.font, 
                              relief="flat",
                              highlightthickness=2)
        
        if self.dtype == datetime:
            self.entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        self.entry.grid(row=1, padx=20, pady=20)
        return self.entry

    def buttonbox(self):
        box = tk.Frame(self)        
        btn_opts = {"font": self.font, "width": 10}
        
        tk.Button(box, text="OK", command=self.ok, **btn_opts).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(box, text="Cancel", command=self.cancel, **btn_opts).pack(side=tk.LEFT, padx=10, pady=10)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def validate(self):
        user_input = self.entry.get()
        try:
            if self.dtype == int: int(user_input)
            elif self.dtype == float: float(user_input)
            elif self.dtype == datetime: datetime.strptime(user_input, "%Y-%m-%d %H:%M")
            return True
        except ValueError:
            messagebox.showerror("Error", f"Invalid {self.dtype.__name__} format.")
            return False

    def apply(self):
        val = self.entry.get()
        self.result = datetime.strptime(val, "%Y-%m-%d %H:%M") if self.dtype == datetime else self.dtype(val)


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    # Editing demonstrations:
    text_val = Edit(root, "Text", "Enter Name:", dtype=str).result
    int_val = Edit(root, "Integer", "Enter Age:", dtype=int).result
    float_val = Edit(root, "Float", "Enter Price:", dtype=float).result
    dt_val = Edit(root, "Date", "Format: YYYY-MM-DD HH:MM", dtype=datetime).result
    print(f"Results: {text_val}, {int_val}, {float_val}, {dt_val}")


