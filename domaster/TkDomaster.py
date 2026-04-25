# MISSION: Full GUI interface to the DOMASTER database.
# STATUS: Research.
# VERSION: 18.2.0
# NOTES: Selected feature updates. Stand alone usage.
# DATE: 2026-04-24 04:14:57
# FILE: TkDomaster.py
# AUTHOR: Randall Nagy
#
# TODO: Make ID columns shorter.
#

import os, sys
if '..' not in sys.path:
    sys.path.insert(0, '..')

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import uuid
import csv
import webbrowser
from datetime import datetime

APP_NAME  = "DoMaster Pro"
FILE_TYPE = ".db"
FILE_ROOT = "domaster" + FILE_TYPE
VERSION   = APP_NAME + " 2026.04.24"
DATA_TYPE = ".options"


class TodoApp:
    def __init__(self, root, database=FILE_ROOT):
        self.root = root
        self.database = database
        self.root.title(f"{APP_NAME} - {VERSION}")
        self.root.geometry("1100x800")
        
        style = ttk.Style()
        style.theme_use("classic") # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
        
        self.hide_completed = tk.BooleanVar(value=False)

        # --- MAIN MENU BAR ---
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Hide Completed Tasks", variable=self.hide_completed, command=self.load_data)


        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import CSV", command=self.import_csv)
        file_menu.add_command(label="Export CSV", command=self.export_csv)
        file_menu.add_command(label="Export HTML", command=self.export_html)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)

        # Tasks Menu
        task_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tasks", menu=task_menu)
        task_menu.add_command(label="Mark Done", command=self.mark_done)
        task_menu.add_command(label="Mark Todo", command=self.mark_undone)
        task_menu.add_command(label="Edit Selected", command=self.open_edit_window)
        task_menu.add_command(label="Delete Task", command=self.delete_task)

        # Help Menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

        # --- Quick Add Bar ---
        input_frame = tk.LabelFrame(root, text="Quick Add Task", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(input_frame, text="Project:").grid(row=0, column=0)
        self.ent_project = tk.Entry(input_frame)
        self.ent_project.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Task:").grid(row=0, column=2)
        self.ent_desc = tk.Entry(input_frame, width=30)
        self.ent_desc.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="Priority:").grid(row=0, column=4)
        self.ent_priority = tk.Entry(input_frame, width=5)
        self.ent_priority.grid(row=0, column=5, padx=5)

        tk.Button(input_frame, text="Add", bg="#28a745", fg="white", command=self.add_task).grid(row=0, column=6, padx=10)

        # --- Global Search ---
        search_frame = tk.Frame(root)
        search_frame.pack(pady=5, fill="x", padx=10)
        tk.Label(search_frame, text="Search All:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.load_data())
        tk.Entry(search_frame, textvariable=self.search_var).pack(side="left", fill="x", expand=True, padx=5)

        # --- Data Table ---
        cols = ("ID", "Project", "Created", "Description", "Priority", "Next")
        self.tree = ttk.Treeview(root, columns=cols, show="headings")
        for col in cols: self.tree.heading(col, text=col)
        self.tree.tag_configure("done", background="#d3d3d3", foreground="#666666")
        self.tree.tag_configure("todo", foreground="blue")
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)

        # Bindings
        self.tree.bind("<Double-1>", lambda e: self.open_edit_window())
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Button-2>", self.show_context_menu)

        # --- Controls Panel ---
        ctrl_frame = tk.Frame(root)
        ctrl_frame.pack(pady=10)
        tk.Button(ctrl_frame, text="Import CSV", width=12, command=self.import_csv).pack(side="left", padx=5)
        tk.Button(ctrl_frame, text="Export CSV", width=12, command=self.export_csv).pack(side="left", padx=5)
        tk.Button(ctrl_frame, text="Export HTML", width=12, command=self.export_html).pack(side="left", padx=5)
        tk.Button(ctrl_frame, text="Mark Done", width=12, command=self.mark_done).pack(side="left", padx=5)
        tk.Button(ctrl_frame, text="Edit Selected", width=12, bg="#007bff", fg="white", command=self.open_edit_window).pack(side="left", padx=5)
        tk.Button(ctrl_frame, text="Delete", width=12, bg="#dc3545", fg="white", command=self.delete_task).pack(side="left", padx=5)

        # Context Menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.open_edit_window)
        self.context_menu.add_command(label="Mark Done", command=self.mark_done)
        self.context_menu.add_command(label="Mark Todo", command=self.mark_undone)

        self.context_menu.add_command(label="Delete", command=self.delete_task)
        
        self.load_data()

    def init_db(self):
        """Initializes the database with the required schema."""
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS todo (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT UNIQUE,
                    project_name TEXT,
                    date_created TEXT,
                    date_done TEXT,
                    task_description TEXT,
                    task_priority INTEGER,
                    next_task TEXT
                );
            """)
            conn.commit()

    def show_about(self):
        messagebox.showinfo("About", f"{APP_NAME}\nVersion: {VERSION}\n\nBuilt with Tkinter & SQLite.")

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path: return
        try:
            with open(file_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                with sqlite3.connect(self.database) as conn:
                    sql = """INSERT OR REPLACE INTO todo 
                             (uuid, project_name, date_created, date_done, task_description, task_priority, next_task) 
                             VALUES (:uuid, :project_name, :date_created, :date_done, :task_description, :task_priority, :next_task)"""
                    conn.executemany(sql, reader)
            self.load_data()
            messagebox.showinfo("Import", "Database synced from CSV.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path: return
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT uuid, project_name, date_created, date_done, task_description, task_priority, next_task FROM todo")
            rows = cursor.fetchall()
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["uuid", "project_name", "date_created", "date_done", "task_description", "task_priority", "next_task"])
            writer.writerows(rows)

    def export_html(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML files", "*.html")])
        if not file_path: return
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ID, project_name, date_created, date_done, task_description, task_priority, next_task FROM todo")
            rows = cursor.fetchall()

        html_content = f"<html><head><title>{APP_NAME} Export</title><style>body{{font-family:sans-serif;margin:40px;}} table{{width:100%;border-collapse:collapse;}} th,td{{padding:12px;border:1px solid #ccc;text-align:left;}} th{{background:#eee;}} .done{{background:#f0f0f0;color:#777;text-decoration:line-through;}} .todo{{color:blue;}}</style></head><body>"
        html_content += f"<h1>{APP_NAME} Report</h1><p>Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p><table><tr><th>ID</th><th>Project</th><th>Created</th><th>Description</th><th>Priority</th><th>Status</th></tr>"
        for row in rows:
            cls = "done" if row[3] else "todo"
            status = "Completed" if row[3] else "Pending"
            html_content += f"<tr class='{cls}'><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{status}</td></tr>"
        html_content += "</table></body></html>"

        with open(file_path, "w", encoding="utf-8") as f: f.write(html_content)
        if messagebox.askyesno("Success", "HTML Exported. Open it?"): webbrowser.open("file://" + os.path.realpath(file_path))

##    def load_data_o(self):
##        if not os.path.exists(self.database):
##            self.init_db()
##            
##        for i in self.tree.get_children(): self.tree.delete(i)
##        sq = f"%{self.search_var.get().strip()}%"
##        with sqlite3.connect(self.database) as conn:
##            cursor = conn.cursor()
##            sql = """SELECT ID, project_name, date_created, task_description, task_priority, next_task, date_done FROM todo 
##                     WHERE (COALESCE(project_name, "") || " " || COALESCE(task_description, "") || " " || COALESCE(uuid, "")) LIKE ?"""
##            cursor.execute(sql, (sq,))
##            for r in cursor.fetchall():
##                tag = "done" if r[6] else "todo"
##                self.tree.insert("", tk.END, values=r[:6], tags=(tag,))


    def load_data(self):
        """Refreshes tree with filtering and priority-based sorting."""
        if not os.path.exists(self.database):
            self.init_db()

        for i in self.tree.get_children(): self.tree.delete(i)
        sq = f"%{self.search_var.get().strip()}%"
        
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            query = """SELECT ID, project_name, date_created, task_description, task_priority, next_task, date_done FROM todo
                       WHERE (project_name || ' ' || task_description) LIKE ?"""
##            query = """SELECT ID, project_name, date_created, task_description, task_priority, next_task, date_done FROM todo 
##                     WHERE (COALESCE(project_name, "") || " " || COALESCE(task_description, "") || " " || COALESCE(uuid, "")) LIKE ?"""

            if self.hide_completed.get():
                query += " AND date_done IS NULL"
            
            # SORTING: Uncompleted first, then by priority (descending 5 to 1)
            query += " ORDER BY project_name DESC, task_priority DESC, ID DESC"
            
            cursor.execute(query, (sq,))
            for r in cursor.fetchall():
                tag = "done" if r[6] else "todo"
                self.tree.insert("", tk.END, values=r[:6], tags=(tag,))

    def add_task(self):
        p, d, pr = self.ent_project.get(), self.ent_desc.get(), self.ent_priority.get()
        if not d: return
        with sqlite3.connect(self.database) as conn:
            conn.execute("INSERT INTO todo (uuid, project_name, date_created, task_description, task_priority) VALUES (?, ?, ?, ?, ?)",
                         (str(uuid.uuid4()), p, datetime.now().strftime("%Y-%m-%d %H:%M"), d, pr))
        self.ent_project.delete(0, tk.END); self.ent_desc.delete(0, tk.END); self.ent_priority.delete(0, tk.END); self.load_data()

    def open_edit_window(self):
        sel = self.tree.selection()
        if not sel: return
        tid = self.tree.item(sel)["values"][0]
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT project_name, task_description, task_priority, next_task FROM todo WHERE ID = ?", (tid,))
            data = cursor.fetchone()

        win = tk.Toplevel(self.root); win.title(f"Edit Task #{tid}"); win.geometry("500x700")
        tk.Label(win, text="Project:").pack(pady=(10,0))
        e_p = tk.Entry(win, width=50); e_p.insert(0, data[0] or ""); e_p.pack(pady=5)
        tk.Label(win, text="Description (Paragraph):").pack(pady=(10,0))
        t_d = tk.Text(win, width=50, height=12); t_d.insert("1.0", data[1] or ""); t_d.pack(pady=5)
        tk.Label(win, text="Priority:").pack(pady=(10,0))
        e_pr = tk.Entry(win, width=50); e_pr.insert(0, data[2] or ""); e_pr.pack(pady=5)
        tk.Label(win, text="Next Task:").pack(pady=(10,0))
        e_n = tk.Entry(win, width=50); e_n.insert(0, data[3] or ""); e_n.pack(pady=5)

        def save():
            with sqlite3.connect(self.database) as conn:
                conn.execute("UPDATE todo SET project_name=?, task_description=?, task_priority=?, next_task=? WHERE ID=?",
                             (e_p.get(), t_d.get("1.0", tk.END).strip(), e_pr.get(), e_n.get(), tid))
            self.load_data(); win.destroy()
        tk.Button(win, text="Save Changes", bg="#28a745", fg="white", command=save, width=20).pack(pady=20)

    def mark_done(self):
        sel = self.tree.selection()
        if not sel: return
        tid = self.tree.item(sel)["values"][0]
        with sqlite3.connect(self.database) as conn:
            conn.execute("UPDATE todo SET date_done = ? WHERE ID = ?", (datetime.now().strftime("%Y-%m-%d %H:%M"), tid))
        self.load_data()

    def mark_undone(self):
        sel = self.tree.selection()
        if not sel: return
        tid = self.tree.item(sel)["values"][0]
        with sqlite3.connect(self.database) as conn:
            conn.execute(f"UPDATE todo SET date_done = NULL WHERE ID = {tid};")
        self.load_data()

    def delete_task(self):
        sel = self.tree.selection()
        if not sel: return
        tid = self.tree.item(sel)["values"][0]
        if messagebox.askyesno("Confirm", "Delete permanently?"):
            with sqlite3.connect(self.database) as conn:
                conn.execute("DELETE FROM todo WHERE ID = ?", (tid,))
            self.load_data()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
