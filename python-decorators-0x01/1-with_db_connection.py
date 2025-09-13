#!/usr/bin/env python3
import sqlite3
import functools

def with_db_connection(func):
    """Decorator that opens and closes a database connection automatically"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")   # ✅ open connection
        try:
            # Pass the connection as the first argument
            return func(conn, *args, **kwargs)
        finally:
            conn.close()  # ✅ always close connection
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

#### Fetch user by ID with automatic connection handling
if __name__ == "__main__":
    user = get_user_by_id(user_id=1)
    print(user)
