#!/usr/bin/env python3
import sqlite3
import functools
from datetime import datetime   # ✅ required for timestamp logging

def log_queries(func):
    """Decorator that logs SQL queries before executing them"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # assume first argument is always the query
        query = args[0] if args else kwargs.get("query", "")
        print(f"[{datetime.now()}] Executing SQL Query: {query}")  # ✅ logs with timestamp
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Example usage
if __name__ == "__main__":
    users = fetch_all_users("SELECT * FROM users")
    print(users)

