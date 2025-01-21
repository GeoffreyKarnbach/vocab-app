import sqlite3

def initialize_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    connection = sqlite3.connect("vocabulary_app.db")
    cursor = connection.cursor()

    # Create Users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """
    )

    # Create Words table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english TEXT NOT NULL,
            romanian TEXT NOT NULL,
            practice_count INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0
        )
        """
    )

    # Create Sessions table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            correct_words INTEGER NOT NULL,
            total_words INTEGER NOT NULL,
            duration INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE
        )
        """
    )

    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Commit changes and close connection
    connection.commit()
    connection.close()

def insert_word(english, romanian):
    connection = sqlite3.connect("vocabulary_app.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO Words (romanian, english, practice_count, correct_count)
        VALUES (?, ?, 0, 0)
        """,
        (english, romanian)
    )

    connection.commit()
    connection.close()

def insert_all_words():
    with open('translations.csv', 'r') as f:
        for line in f:
            english, romanian = line.strip().split(';')
            insert_word(english, romanian)


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
    insert_all_words()
