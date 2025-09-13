#!/usr/bin/env python3
import sqlite3

class ExecuteQuery:
    """Custom context manager that executes a query with parameters"""
    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params if params else ()
        self.conn = None
        self.cursor = None
        self.results = None

    def __enter__(self):
        # Open DB connection
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        # Execute query with params
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()

        return self.results  # ✅ results available directly inside with-block

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Ensure commit/rollback and close connection
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

        return False  # Don’t suppress exceptions

# ✅ Example usage
if __name__ == "__main__":
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)

    with ExecuteQuery("users.db", query, params) as results:
        print("Users older than 25:")
        for row in results:
            print(row)
