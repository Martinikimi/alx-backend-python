#!/usr/bin/env python3
import sqlite3
import functools

def with_db_connection(func):
    """Decorator that opens and closes a database connection automatically"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")   # open DB
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()  # always close DB
    return wrapper

def transactional(func):
    """Decorator that wraps a function in a transaction"""
    @functools.wraps(func)
    de
