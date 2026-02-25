# MISSION: Create a reusable GUITUI Framework.
# STATUS: Research
# VERSION: 0.0.0
# NOTES: GUI default.
# DATE: 2026-02-21 03:08:38
# FILE: tui_calendar.py
# AUTHOR: Randall Nagy
#
import calendar
import datetime

def get_calendar(month=None, year=None)->list:
    if not year:
        year = datetime.datetime.now().year
        
    if not month:
        month = datetime.datetime.now().month
        
    if not (1 <= month <= 12):
        return ["Invalid month number:",
                "Month numbers are",
                "from 1 to 12."]
    
    if not (1<= year <= 9999):
        return ["Invalid year number:",
                "Year numbers are",
                "from 1 to 9999."]
    
    # return the multiline string calendar, or error.
    try:
        month_calendar = calendar.month(year, month)
        return [month_calendar]
    except:
        return ['Bad number format(s)']

if __ame__== "__ain__:
    for line in get_calendar(12,10000):
        print(line)
    print()
    for line in get_calendar(122,1978):
        print(line)
    print()    
    for line in get_calendar(12,1978):
        print(line)
    for line in get_calendar():
        print(line)
    print()
