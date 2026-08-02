"""
utils/validators.py
Reusable input validation for auth forms and file uploads.
"""

import re
import os

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,30}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_signup_data(data: dict):
    """Returns (is_valid: bool, errors: dict)."""
    errors = {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    email = (data.get("email") or "").strip()

    if not username:
        errors["username"] = "Username is required."
    elif not USERNAME_PATTERN.match(username):
        errors["username"] = "Username must be 3-30 characters (letters, numbers, underscore only)."

    if not password:
        errors["password"] = "Password is required."
    elif len(password) < 8:
        errors["password"] = "Password must be at least 8 characters long."

    if email and not EMAIL_PATTERN.match(email):
        errors["email"] = "Please enter a valid email address."

    return (len(errors) == 0), errors


def validate_login_data(data: dict):
    errors = {}
    if not (data.get("username") or "").strip():
        errors["username"] = "Username is required."
    if not (data.get("password") or ""):
        errors["password"] = "Password is required."
    return (len(errors) == 0), errors


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_extensions


def safe_filename(filename: str) -> str:
    """Strip directory components and unsafe characters from a filename."""
    filename = os.path.basename(filename)
    filename = re.sub(r"[^A-Za-z0-9_.\-]", "_", filename)
    return filename
