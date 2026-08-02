"""
routes/upload_routes.py
Handles campaign CSV uploads. The route only deals with the HTTP
file transfer and validation; all data processing happens in
services/analytics_engine.py.
"""

import os
import logging
import uuid

from flask import Blueprint, request, session, current_app

from config import get_config
from utils.validators import allowed_file, safe_filename
from utils.auth_decorators import login_required
from utils.response_helpers import success_response, error_response
from services.analytics_engine import analyze_dataset, AnalyticsError
from services.report_service import save_dataset_record

logger = logging.getLogger(__name__)
upload_bp = Blueprint("upload", __name__)
config = get_config()


@upload_bp.route("/upload", methods=["POST"])
@login_required
def upload_file():
    if "file" not in request.files:
        return error_response("No file was included in the request.", 400)

    file = request.files["file"]

    if file.filename == "":
        return error_response("No file was selected.", 400)

    if not allowed_file(file.filename, config.ALLOWED_UPLOAD_EXTENSIONS):
        return error_response("Only CSV files are supported in Version 1.0.", 415)

    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

    original_name = safe_filename(file.filename)
    stored_name = f"{session['user_id']}_{uuid.uuid4().hex[:8]}_{original_name}"
    stored_path = os.path.join(config.UPLOAD_FOLDER, stored_name)

    try:
        file.save(stored_path)
        analysis = analyze_dataset(stored_path)
    except AnalyticsError as err:
        # Clean up the bad file so uploads/ doesn't fill with junk
        if os.path.exists(stored_path):
            os.remove(stored_path)
        return error_response(str(err), 422)
    except Exception:
        logger.exception("Unexpected error while processing upload")
        if os.path.exists(stored_path):
            os.remove(stored_path)
        return error_response(
            "Unable to process this file. Please check the required columns and try again.", 500
        )

    dataset_id = save_dataset_record(
        user_id=session["user_id"],
        original_filename=original_name,
        stored_filename=stored_name,
        row_count=analysis["row_count"],
    )

    analysis["dataset_id"] = dataset_id
    return success_response(analysis, "File uploaded and processed successfully.")
