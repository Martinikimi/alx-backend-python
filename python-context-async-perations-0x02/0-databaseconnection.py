#!/usr/bin/env python3
import sqlite3

class DatabaseConnection:
    """Custom context manager for handling SQLite DB connections"""
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        # Open the connection when entering the context
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the connection when exiting the context
        if self.conn:
            if exc_type is None:
                self.conn.commit()   # ✅ commit if no error
            else:
                self.conn.rollback() # ❌ rollback if error
            self.conn.close()
        # Returning False means exceptions are not suppressed
        return False

# ✅ Using the context manager
if __name__ == "__main__":
    with DatabaseConnection("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        print(results)
