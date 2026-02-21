# MISSION: Create a reusable GUITUI Framework.
# STATUS: Research
# VERSION: 0.0.0
# NOTES: GUI default.
# DATE: 2026-02-21 02:45:21
# FILE: gui_relate.py
# AUTHOR: Randall Nagy
#
import tkinter as tk
from tkinter import ttk

class TaskChild:
    def __init__(self, name):
        self.name = name

class TaskParent:
    def __init__(self, name):
        self.name = name
        self.child_ids = []  # Stores id() of TaskChilds

class TaskLinker:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Linker")

        # Data Storage
        self.parents = [TaskParent("Documents"), TaskParent("Images")]
        self.children = [TaskChild("report.pdf"), TaskChild("photo.jpg"), TaskChild("notes.txt")]
        self.id_map = {id(f): f for f in self.children}
        self.id_map.update({id(f): f for f in self.parents})

        # --- UI Setup ---
        # Task Listbox (Unassigned Tasks)
        tk.Label(root, text="Unassigned Tasks").grid(row=0, column=0)
        self.task_listbox = tk.Listbox(root, height=10)
        self.task_listbox.grid(row=1, column=0, padx=10, pady=10)

        # Folder Treeview (Hierarchical View)
        tk.Label(root, text="Task Treeview").grid(row=0, column=2)
        self.tree = ttk.Treeview(root, show="tree")
        self.tree.grid(row=1, column=2, padx=10, pady=10)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.grid(row=1, column=1)
        ttk.Button(btn_frame, text="Add to Task >>", command=self.add_to_parent).pack(pady=5)
        ttk.Button(btn_frame, text="<< Remove Task", command=self.remove_from_parent).pack(pady=5)

        self.refresh_ui()

    def refresh_ui(self):
        # Update Listbox
        self.task_listbox.delete(0, tk.END)
        linked_ids = [fid for folder in self.parents for fid in folder.child_ids]
        for f in self.children:
            if id(f) not in linked_ids:
                self.task_listbox.insert(tk.END, f.name)

        # Update Treeview
        self.tree.delete(*self.tree.get_children())
        for folder in self.parents:
            folder_iid = str(id(folder))
            self.tree.insert("", "end", iid=folder_iid, text=folder.name, open=True)
            for task_id in folder.child_ids:
                task_obj = self.id_map[task_id]
                self.tree.insert(folder_iid, "end", iid=str(task_id), text=task_obj.name)

    def add_to_parent(self):
        selection = self.task_listbox.curselection()
        tree_sel = self.tree.selection()
        
        if selection and tree_sel:
            # Find the selected Task object
            unlinked_Tasks = [f for f in self.children if id(f) not in 
                             [fid for folder in self.parents for fid in folder.child_ids]]
            task_obj = unlinked_Tasks[selection[0]]
            
            # Find the target parent
            target_iid = tree_sel[0]
            target_obj = self.id_map.get(int(target_iid))
            
            if isinstance(target_obj, TaskParent):
                target_obj.child_ids.append(id(task_obj))
                self.refresh_ui()

    def remove_from_parent(self):
        selection = self.tree.selection()
        if selection:
            task_id = int(selection[0])
            for folder in self.parents:
                if task_id in folder.child_ids:
                    folder.child_ids.remove(task_id)
                    self.refresh_ui()
                    break

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskLinker(root)
    root.mainloop()
