# DoMaster 🛠️

**DoMaster** is a robust, lightweight Console Terminal User Interface (TUI) task manager built with Python and SQLite. It is designed for high-performance, keyboard-driven workflows to manage complex projects with task dependencies and detailed reporting.

## 🌟 STATUS
Good to go!

## 🌟 Features

- **Local Persistence**: Powered by an SQLite3 backend for rapid data access and reliability.
- **Project-Centric**: Organize tasks by `project_name` with integrated priority levels.
- **Task Dependencies**: Link tasks together using the `next_task` ID field.
- **Smart Sync**: Import CSV or Tab-Delimited files with automated conflict resolution; existing UUIDs are updated while new ones are inserted.
- **Comprehensive Reporting**: 
  - **Pending Report**: HTML export grouped by project and ordered by priority.
  - **Completion Report**: HTML export grouped by date and ordered by completion time.
- **Database Mobility**: Built-in functions to dump, empty, and load database files with 2026-compliant timestamps.

## 📊 Database Schema (Table: `todo`)

| Field | Type | Description |
| :--- | :--- | :--- |
| `ID` | Integer | Primary Key (Auto-increment). |
| `uuid` | Text | **Immutable** Unique Identifier (Generated on creation). |
| `project_name` | Text | Name of the parent project. |
| `date_created` | Text | ISO-8601 Timestamp of creation. |
| `date_done` | Text | ISO-8601 Timestamp of completion. |
| `task_description`| Text | Full description of the task. |
| `task_priority` | Integer | Numerical priority (Lower = Higher priority). |
| `next_task` | Integer | Reference to the next task `ID` (Defaults to 0). |

## 🚀 Installation

More than one way to enjoy the do-master:

### ✌️Either: 

👉 **Clone the repository**:
```
bash
git clone https://github.com
cd domaster
python ./domaster.py
```

👉 **Otherwise**
```
python -m pip install whatever.whl
python -m domaster
```





