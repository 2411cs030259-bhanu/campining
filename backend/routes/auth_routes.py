"""
routes/auth_routes.py
HTTP layer for authentication. Routes stay thin: parse the request,
call the service layer, translate the result into a JSON response.
"""

import logging

from flask import Blueprint, request, session

from services.auth_service import signup_user, authenticate_user, AuthError
from utils.validators import validate_signup_data, validate_login_data
from utils.response_helpers import success_response, error_response

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}

    is_valid, errors = validate_signup_data(data)
    if not is_valid:
        return error_response("Please fix the errors below.", 422, errors)

    try:
        user = signup_user(
            username=data["username"],
            password=data["password"],
            email=data.get("email"),
        )
    except AuthError as err:
        return error_response(str(err), 409)
    except Exception:
        logger.exception("Unexpected error during signup")
        return error_response("Unable to create your account right now. Please try again.", 500)

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session.permanent = True

    return success_response(user, "Account created successfully.", 201)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    is_valid, errors = validate_login_data(data)
    if not is_valid:
        return error_response("Please fix the errors below.", 422, errors)

    try:
        user = authenticate_user(data["username"], data["password"])
    except AuthError as err:
        return error_response(str(err), 401)
    except Exception:
        logger.exception("Unexpected error during login")
        return error_response("Unable to log in right now. Please try again.", 500)

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session.permanent = True

    return success_response(user, "Logged in successfully.")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return success_response(message="Logged out successfully.")


@auth_bp.route("/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return error_response("Not authenticated.", 401)
    return success_response({"id": session["user_id"], "username": session["username"]})
