"""
services/auth_service.py
Business logic for signup and login. Kept separate from routes so
the logic can be reused (and later swapped to JWT-based auth in a
future version) without touching the Flask route handlers.
"""

from werkzeug.security import generate_password_hash, check_password_hash

from models.user_model import create_user, get_user_by_username, username_exists


class AuthError(Exception):
    """Raised for expected auth failures (bad credentials, duplicate user)."""
    pass


def signup_user(username: str, password: str, email: str = None) -> dict:
    username = username.strip()
    email = email.strip() if email else None

    if username_exists(username):
        raise AuthError("This username is already taken.")

    password_hash = generate_password_hash(password)
    user_id = create_user(username=username, email=email, password_hash=password_hash)

    return {"id": user_id, "username": username, "email": email}


def authenticate_user(username: str, password: str) -> dict:
    user = get_user_by_username(username.strip())
    if not user or not check_password_hash(user["password_hash"], password):
        raise AuthError("Invalid username or password.")

    return {"id": user["id"], "username": user["username"], "email": user.get("email")}
