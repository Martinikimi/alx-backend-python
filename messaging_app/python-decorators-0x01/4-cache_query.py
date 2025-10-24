#!/usr/bin/env python3
import time
import sqlite3
import functools

query_cache = {}

def with_db_connection(func):
    """Decorator that opens and closes a database connection automatically"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

def cache_query(func):
    """Decorator that caches query results to avoid redundant DB calls"""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        # Assume the query is always passed as a kwarg or 1st positional arg
        query = kwargs.get("query") or (args[0] if args else None)

        if query in query_cache:
