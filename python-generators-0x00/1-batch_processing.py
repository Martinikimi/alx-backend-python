#!/usr/bin/python3
import mysql.connector

def stream_users_in_batches(batch_size):
    """
    Generator that fetches rows from user_data table in batches.
    Yields a list of users of size batch_size.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_mysql_password",  # Replace with your MySQL password
            database="ALX_prodev"
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")

        batch = []
        for row in cursor:  # Loop #1
            batch.append(row)
            if len(batch) == batch_size:
                yield batch  # Yield the batch
                batch = []
        if batch:
            yield batch  # Yield remaining users

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def batch_processing(batch_size):
    """
    Generator that processes batches and yields users with age > 25.
    """
    for batch in stream_users_in_batches(batch_size):  # Loop #2
        for user in batch:  # Loop #3
            if user['age'] > 25:
                yield user
