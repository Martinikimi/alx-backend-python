import mysql.connector
from mysql.connector import Error

try:
    # Connect to MySQL server
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='$X2gN#8tVzP@1kR%3bQ^9hLmW!7dS*4yT&0uF+eZ6jC'  
    )

    if connection.is_connected():
        cursor = connection.cursor()
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS alxbookstore")
        print("Database 'alxbookstore' created successfully!")

except Error as e:
    print("Error while connecting to MySQL:", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()




