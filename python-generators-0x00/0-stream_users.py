#!/usr/bin/python3
import mysql.connector

def stream_users():
    """
    Generator that streams rows from the user_data table one by one.
    Each row is returned as a dictionary with column names as keys.
    """
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_mysql_password",  # Replace with your MySQL password
            database="ALX_prodev"
        )
        cursor = connection.cursor(dictionary=True)

        # Execute query to fetch all users
        cursor.execute("SELECT * FROM user_data")

        # Yield rows one by one
        row = cursor.fetchone()
        while row:
            yield row
            row = cursor.fetchone()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

