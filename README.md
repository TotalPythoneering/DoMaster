# DoMaster 🛠️

**DoMaster** is a robust, lightweight task manager built with Python and SQLite. It is designed for high-performance, keyboard-driven workflows to manage complex projects with task dependencies and detailed reporting.

Forever free & open **DoMaster** allows us to manage any infinite list of actionable-items either in the (1) present working directory, or in the (2) single GLOBAL database ... (*)

## 🌟NEW!

👉 Available on [PyPy.org](https://pypi.org/project/domaster/) we can now install the latest release of DoMaster using:

```pip install domaster```


## 🌟 The GuiTui (TuiGui?) Experience
👉 The "GuiTui" concept.

Here is a video on how to [download the code](https://youtu.be/xYsrTbXEBhM) and try the new ***G.U.I*** user interface where Tkinter is installed, yet preserve the ***T.U.I*** experience whenever its not.

To review the GuiTui concept:

✔️ Download & unzip the code.

✔️ Change to the parent directory of the **domaster** folder.

✔️ python -m domaster

~ or ~

✔️ python3 -m domaster


## 🌟 Features

- **Local Persistence**: Powered by an SQLite3 backend for rapid data access and reliability.
- **Project-Centric**: Organize tasks by `project_name` with integrated priority levels.
- **Task Dependencies**: Link tasks together using the `next_task` ID field.
- **Smart Sync**: Import CSV or Tab-Delimited files with automated conflict resolution; existing UUIDs are updated while new ones are inserted.
- **Comprehensive Reporting**: 
  - **Pending Report**: HTML export grouped by project and ordered by priority.
  - **Completion Report**: HTML export grouped by date and ordered by completion time.
- **Database Mobility**: Built-in functions to dump, empty, and load database files with 2026-compliant timestamps.
- **Database Backup**: Supports on-demand and automatic on-exit GLOBAL database backups.

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

## 🌟User Interfaces
Far too handy to deprive DevOps, developers, or power-user 'pros of any important do-list-manager **DoMaster** sports an unheard-of total of three (3) user interfaces: 

(1) The pure TUI to support 'Ops personnel:

```DoMaster```

(2) The TuiGui to use the same TUI metaphor whenever we've a GUI empestered:

```DoMaster```

(3) The GUI mode to enjoy the classic Xerox / PARC / Mac / Windows / XWindows experience:

``` TkDo ```

~ or ~

```python -m domaster.tkdo```

🪄All using the same database format and nexus, of course. 🤓

 
👉 A new **database backup** feature can now clone our GLOBAL database to another location.

## 🌟 STATUS
Good to go. Use the 'pip installer in the dist folder.

Here is a [primer video](https://youtu.be/Xg3zdm0wZ7I).

Here is the 'vdoc for the [new backup feature](https://www.youtube.com/shorts/2j7lk9PRjyE).

🎓 **Notes:** 

👉 The GLOBAL / PACKAGE database is the default. 

👉 TUI-toggling the LOCAL database will put the same into wherever we choose to run `python -m domaster` ... !

👉 Both the HTML Reports & CSV Exports are ALWAYS put into the LOCAL (`pwd`) Db. (*)


Happy 'Spire-ring!

-- Randall
🫡 

(*) and yes, with care we might even *export* from one `Db` to *import* into the other.









