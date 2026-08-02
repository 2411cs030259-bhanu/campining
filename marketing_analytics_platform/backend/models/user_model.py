"""
models/user_model.py
Data-access layer for the `users` table.

Routes and services should call these functions instead of writing
raw SQL inline, so the query logic lives in exactly one place.
"""

from database import get_db_cursor


def create_user(username: str, email: str, password_hash: str) -> int:
    """Insert a new user. Returns the new user's id."""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            (username, email, password_hash),
        )
        return cursor.lastrowid


def get_user_by_username(username: str):
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE username = %s",
            (username,),
        )
        return cursor.fetchone()


def get_user_by_id(user_id: int):
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT id, username, email, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        return cursor.fetchone()


def username_exists(username: str) -> bool:
    return get_user_by_username(username) is not None
