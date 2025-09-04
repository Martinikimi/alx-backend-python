#!/usr/bin/python3
import seed

def stream_user_ages():
    """
    Generator that yields user ages one by one from the user_data table.
    """
    connection = None
    cursor = None
    try:
        connection = seed.connect_to_prodev()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT age FROM user_data")

        for row in cursor:  # Loop #1
            yield row['age']

    except Exception as err:
        print(f"Error: {err}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def calculate_average_age():
    """
    Calculates and prints the average age using the stream_user_ages generator.
    """
    total_age = 0
    count = 0
    for age in stream_user_ages():  # Loop #2
        total_age += age
        count += 1

    if count > 0:
        average = total_age / count
        print(f"Average age of users: {average}")
    else:
        print("No users found.")


if __name__ == "__main__":
    calculate_average_age()
