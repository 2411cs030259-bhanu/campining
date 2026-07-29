"""
utils/response_helpers.py
Standardized JSON response shapes so every endpoint returns a
consistent structure the frontend can rely on.
"""

from flask import jsonify


def success_response(data=None, message="Success", status_code=200):
    payload = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def error_response(message="Something went wrong. Please try again.", status_code=400, errors=None):
    payload = {"success": False, "message": message}
    if errors:
        payload["errors"] = errors
    return jsonify(payload), status_code
