from datetime import datetime
import sqlite3

DATABASE = "dexa.db"


# Create and return a SQLite database connection with row access and foreign keys enabled
def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# Initialize tables and insert default user if not present
def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL DEFAULT 'New Chat',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("SELECT id FROM users LIMIT 1")
    user = cursor.fetchone()

    if user is None:
        cursor.execute(
            "INSERT INTO users (name, created_at) VALUES (?, ?)",
            ("Deepa", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )

    connection.commit()
    connection.close()


# Retrieve the primary user ID from the database
def get_user_id():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM users LIMIT 1")
    user = cursor.fetchone()

    connection.close()

    if user:
        return user["id"]
    return None


# Create a new chat session for the current user
def create_session(title="New Chat"):
    connection = get_connection()
    cursor = connection.cursor()

    user_id = get_user_id()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO chat_sessions (user_id, title, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, title, now, now),
    )

    session_id = cursor.lastrowid
    connection.commit()
    connection.close()

    return session_id


# Retrieve all chat sessions sorted by most recently updated
def get_sessions():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, title, created_at, updated_at
        FROM chat_sessions
        ORDER BY updated_at DESC
    """)

    sessions = cursor.fetchall()
    connection.close()
    return sessions


# Retrieve a single chat session by ID
def get_session(session_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, title, created_at, updated_at FROM chat_sessions WHERE id = ?",
        (session_id,),
    )

    session = cursor.fetchone()
    connection.close()
    return session


# Insert a message into a session and update the session timestamp
def save_message(session_id, role, content):
    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO chat_messages (session_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (session_id, role, content, now),
    )

    cursor.execute(
        "UPDATE chat_sessions SET updated_at = ? WHERE id = ?",
        (now, session_id),
    )

    connection.commit()
    connection.close()


# Retrieve all messages for a specific chat session in chronological order
def get_messages(session_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, role, content, created_at
        FROM chat_messages
        WHERE session_id = ?
        ORDER BY id ASC
        """,
        (session_id,),
    )

    messages = cursor.fetchall()
    connection.close()
    return messages


# Retrieve the most recent N messages for context window management
def get_recent_messages(session_id, limit=20):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT role, content
        FROM chat_messages
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (session_id, limit),
    )

    messages = cursor.fetchall()
    connection.close()
    return list(reversed(messages))


# Update the title of an existing chat session
def update_session_title(session_id, title):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE chat_sessions SET title = ? WHERE id = ?",
        (title, session_id),
    )

    connection.commit()
    connection.close()


# Delete a specific chat session and its cascading messages
def delete_session(session_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))

    connection.commit()
    connection.close()


# Delete all chat sessions and wipe conversation history
def clear_all_history():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM chat_sessions")

    connection.commit()
    connection.close()