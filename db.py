import sqlite3
from datetime import datetime


def get_connection():
    return sqlite3.connect("notas.db")


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS users  (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        name TEXT,
        created_at TEXT
    )
"""
    )

    cursor.execute(
        "CREATE TABLE OF NOT EXISTS notes (" \
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "title TEXT," \
        "text TEXT,"
        "status TEXT," \
        "created_ad TEXT," \
        "user_id INTEGER," \
        "FOREING KEY(user_id) REFERENCES users(id)"
        ")"           
    )

    conn.commit()
    conn.close()


def get_or_create_user(tg_id: int, name: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (tg_id,))
    row = cursor.fetchone()

    if row:
        conn.close()
        return row[0]

    cursor.execute(
        "INSERT INTO users (telegram_id, name, created_at) VALUES (?, ?, ?)",
        (tg_id, name, datetime.now().isoformat()),
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return user_id


def create_note(user_id, title, text) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO notes (title, text, status, created_ad, user_id) VALUES (?, ?, ?, ?, ?)",
        (title, text, "Active", datetime.now().isoformat(), user_id),
    )

    note_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return note_id


def get_notes(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, text FROM notes WHERE user_id = ? AND status = 'Active'", (user_id, )
    )
    rows = cursor.fetchall()

    conn.close()

    return rows


def arhive_note(note_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE notes SET status = 'Archived' WHERE id = ?", (note_id, )
    )
    updated = cursor.rowcount

    conn.commit()
    conn.close()

    return updated > 0


def delete_note(note_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM notes WHERE id = ?", (note_id, )
    )
    updated = cursor.rowcount

    conn.commit()
    conn.close()

    return updated > 0
