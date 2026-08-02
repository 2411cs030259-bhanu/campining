"""
utils/auth_decorators.py
Shared decorator to protect routes that require an authenticated session.
"""

from functools import wraps
from flask import session

from utils.response_helpers import error_response


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return error_response("Please log in to continue.", 401)
        return view_func(*args, **kwargs)
    return wrapped
