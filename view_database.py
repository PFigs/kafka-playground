import sqlite3
from context import topics


def main():
    """ Views the database content """
    connection = sqlite3.connect("kafka.db")
    cursor = connection.cursor()
    for topic in topics:
        cursor.execute(f"SELECT * from {topic}")
        print(cursor.fetchall())


if __name__ == "__main__":
    main()
