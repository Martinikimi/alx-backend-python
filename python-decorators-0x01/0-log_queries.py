import sqlite3
import functools

# Decorator to log SQL queries
def log_queries(func):
    @functools.wraps(func)   
    def wrapper(query, *args, **kwargs):
        print(f"[LOG] Executing SQL query: {query}")
        return func(query, *args, **kwargs)  
    return wrapper

@log_queries
def fetch_all_users(query):
    """Fetch all users from the database using the given query."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

users = fetch_all_users("SELECT * FROM users")
print(users)
