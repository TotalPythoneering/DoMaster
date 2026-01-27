# MISSION: Hoist yet another to-do manager 'ore Modern Python.
# STATUS: Research
# VERSION: 1.2.0
# NOTES: Official T.U.I in-our-face. :^)
# DATE: 2026-01-27 09:23:15
# FILE: __main__.py
# AUTHOR: Randall Nagy
#
from . main import mainloop
from . upsert import UpsertSqlite
from . sync_tool import SQLiteCSVSync

mainloop()
