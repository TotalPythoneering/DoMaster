# MISSION: Manage a to-do list or / and ideas.
# STATUS: Release
# VERSION: 1.1.1
# NOTES: Tested. See the project for full documentation.
# DATE: 2026-01-27 09:03:30
# FILE: upsert.py
# AUTHOR: Randall Nagy
#
class UpsertSqlite:
    
    @staticmethod
    def JunkId(row)->dict:
        nope = 'ID', 'id', 'Id'
        if isinstance(row, dict):
            for ix in nope:
                if ix in row:
                    del row[ix]
        elif isinstance(row, list):
            copy = list(nope)
            for ix in nope:
                if ix in row:
                    row.remove(ix)
        return row

    @staticmethod
    def EncodeUpsert(table_name:str, row:dict)->str:
        ''' Encode a dynamic UPSERT ON CONFLICT clause. '''
        if 'uuid' not in row:
            raise ValueError(
                f"Table [{table_name}] missing 'uuid' column.")
        
        row = UpsertSqlite.JunkId(row)
                
        placeholders = ", ".join(["?"] * len(row))
        column_names = ", ".join(row.keys())
        insert_values = tuple(row.values())
        update_set = ", ".join(
            [f"{col} = excluded.{col}" for col in row if col != 'uuid'])

        upsert_sql = f"""
            INSERT INTO {table_name} ({column_names})
            VALUES {insert_values}
            ON CONFLICT(uuid) DO UPDATE SET {update_set}
        """
        return upsert_sql

    @staticmethod
    def OrderKeys(obj):
        ''' Dynamic Upserting requires? '''
        if isinstance(obj, dict):
            for key in sorted(obj.keys()):
                result[key] = obj[key]
            return result
        elif isinstance(obj, list):
            return sorted(obj)
        return obj
    
    @staticmethod
    def EncodeUpsertSet(table_name: str, row: dict) -> tuple:
        ''' Generates a parameterized UPSERT string
            and its associated values. This version
            generates a safe SQL string with ?
            placeholders and returns both the query
            and the data tuple.

        Why this is better for your 2026 project:
            * SQL Injection Protection: By using ?
            placeholders, the database engine handles
            the sanitization of strings, preventing
            malicious code injection.

            * Type Handling: SQLite will correctly handle
            None (NULL), integers, and floats without you
            having to manually format them into a string.
            
            * Efficiency: Parameterized queries allow the
            SQLite engine to "compile" the query once and
            reuse the plan, which is faster for bulk imports.
            
            * Special Characters: It correctly handles quotes,
            backslashes, and emojis within your address or name
            fields that would otherwise break a raw string.
        '''
        if 'uuid' not in row:
            raise ValueError(f"Table [{table_name}] missing 'uuid' column.")

        row = UpsertSqlite.JunkId(row)
            
        column_names = ", ".join(row.keys())
        # Create placeholders like (?, ?, ?)
        placeholders = ", ".join(["?"] * len(row))
        
        # Create the update clause: col1 = excluded.col1, col2 = excluded.col2...
        update_set = ", ".join(
            [f"{col} = excluded.{col}" for col in row if col != 'uuid']
        )

        upsert_sql = f"""
            INSERT INTO {table_name} ({column_names})
            VALUES ({placeholders})
            ON CONFLICT(uuid) DO UPDATE SET {update_set}
        """
        
        # Return both the query and the values to be
        # passed to cursor.execute()
        return upsert_sql, tuple(row.values())
