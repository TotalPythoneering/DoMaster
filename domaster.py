import sqlite3
import uuid
import csv
import datetime
import os

DB_NAME = "domaster.db"

def get_now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS todo (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE,
                project_name TEXT,
                date_created TEXT,
                date_done TEXT,
                task_description TEXT,
                task_priority INTEGER,
                next_task INTEGER DEFAULT 0
            )
        """)

def add_task():
    print("\n--- Add New Task ---")
    proj = input("Project Name: ")
    desc = input("Description: ")
    pri = input("Priority (Integer): ")
    next_t = input("Next Task ID (Default 0): ") or 0
    
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""INSERT INTO todo (uuid, project_name, date_created, task_description, task_priority, next_task) 
                     VALUES (?, ?, ?, ?, ?, ?)""", 
                     (str(uuid.uuid4()), proj, get_now(), desc, pri, next_t))
    print("Task added successfully.")

def update_task():
    tid = input("Enter ID to update: ")
    fields = ["project_name", "task_description", "task_priority", "next_task", "date_done"]
    print("Available fields:", ", ".join(fields))
    field = input("Field to update: ")
    new_val = input(f"New value for {field}: ")
    
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(f"UPDATE todo SET {field} = ? WHERE ID = ?", (new_val, tid))

def mark_done():
    tid = input("Enter Task ID to mark as done: ")
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("UPDATE todo SET date_done = ? WHERE ID = ?", (get_now(), tid))

def list_tasks(filter_type="all"):
    query = "SELECT ID, project_name, task_description, task_priority, date_created, date_done FROM todo"
    if filter_type == "pending": query += " WHERE date_done IS NULL OR date_done = ''"
    elif filter_type == "done": query += " WHERE date_done IS NOT NULL AND date_done != ''"
    
    query += " ORDER BY project_name ASC, task_priority ASC"
    
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute(query).fetchall()
        print(f"\n{'ID':<4} | {'Project':<15} | {'Description':<25} | {'Pri':<4} | {'Created'}")
        print("-" * 80)
        for r in rows:
            print(f"{r[0]:<4} | {r[1]:<15} | {r[2]:<25} | {r[3]:<4} | {r[4]}")

def export_html(status="pending"):
    filename = f"report_{status}_{datetime.date.today()}.html"
    with sqlite3.connect(DB_NAME) as conn:
        if status == "pending":
            rows = conn.execute("SELECT project_name, task_description, task_priority, date_created FROM todo WHERE date_done IS NULL ORDER BY project_name, task_priority").fetchall()
            group_field = 0 # project_name
        else:
            rows = conn.execute("SELECT date_done, project_name, task_description, task_priority FROM todo WHERE date_done IS NOT NULL ORDER BY date_done DESC").fetchall()
            group_field = 0 # date_done

    with open(filename, "w") as f:
        f.write(f"<html><body><h1>DoMaster {status.capitalize()} Report</h1>")
        current_group = None
        for r in rows:
            if r[group_field] != current_group:
                current_group = r[group_field]
                f.write(f"<h2>{current_group}</h2>")
            f.write(f"<p>{r[1]} - Priority: {r[2]} (Created: {r[3] if status=='pending' else ''})</p>")
        f.write("</body></html>")
    print(f"Report exported to {filename}")

def import_file(filename, delimiter):
    with open(filename, 'r') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        with sqlite3.connect(DB_NAME) as conn:
            for row in reader:
                conn.execute("""
                    INSERT INTO todo (uuid, project_name, date_created, date_done, task_description, task_priority, next_task)
                    VALUES (:uuid, :project_name, :date_created, :date_done, :task_description, :task_priority, :next_task)
                    ON CONFLICT(uuid) DO UPDATE SET
                        project_name=excluded.project_name,
                        date_done=excluded.date_done,
                        task_description=excluded.task_description,
                        task_priority=excluded.task_priority,
                        next_task=excluded.next_task
                """, row)

def main_menu():
    init_db()
    while True:
        print("\n--- DoMaster TUI ---")
        print("1. Add Task    2. Update Task    3. Mark Done    4. List Pending")
        print("5. List Done   6. List All       7. Projects     8. Export HTML")
        print("9. CSV Import  10. DB Backup     11. Exit")
        choice = input("Selection: ")
        
        if choice == '1': add_task()
        elif choice == '2': update_task()
        elif choice == '3': mark_done()
        elif choice == '4': list_tasks("pending")
        elif choice == '5': list_tasks("done")
        elif choice == '6': list_tasks("all")
        elif choice == '7':
            with sqlite3.connect(DB_NAME) as conn:
                projs = conn.execute("SELECT DISTINCT project_name FROM todo ORDER BY project_name").fetchall()
                for p in projs: print(f"- {p[0]}")
        elif choice == '8': 
            export_html("pending")
            export_html("done")
        elif choice == '11': break

if __name__ == "__main__":
    main_menu()
