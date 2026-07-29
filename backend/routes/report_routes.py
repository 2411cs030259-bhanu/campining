"""
routes/report_routes.py
Generates and serves downloadable analytics reports.

Version 1.0 keeps this stateless on the analysis side: the frontend
already has the processed analysis (returned from /upload), and
sends it back here to be turned into a CSV file. This avoids
re-processing the dataset and keeps the report generation logic
in one place (services/report_service.py).
"""

import os
import logging

from flask import Blueprint, request, session, send_from_directory

from config import get_config
from utils.auth_decorators import login_required
from utils.response_helpers import success_response, error_response
from services.report_service import build_report_csv, save_report_record, list_reports_for_user

logger = logging.getLogger(__name__)
report_bp = Blueprint("report", __name__)
config = get_config()


@report_bp.route("/download", methods=["POST"])
@login_required
def download_report():
    payload = request.get_json(silent=True) or {}
    analysis = payload.get("analysis")
    dataset_id = payload.get("dataset_id")

    if not analysis or "kpis" not in analysis:
        return error_response("No analysis data was provided to build a report.", 400)

    try:
        filename = build_report_csv(analysis, user_id=session["user_id"])
        save_report_record(
            user_id=session["user_id"],
            dataset_id=dataset_id,
            report_filename=filename,
            kpis=analysis["kpis"],
        )
    except Exception:
        logger.exception("Unexpected error while building report")
        return error_response("Unable to generate the report right now. Please try again.", 500)

    return success_response({"filename": filename}, "Report generated successfully.")


@report_bp.route("/reports/<path:filename>", methods=["GET"])
@login_required
def serve_report(filename):
    # Only allow downloading reports belonging to the current user
    if not filename.startswith(f"report_{session['user_id']}_"):
        return error_response("Report not found.", 404)

    if not os.path.exists(os.path.join(config.REPORT_FOLDER, filename)):
        return error_response("Report not found.", 404)

    return send_from_directory(config.REPORT_FOLDER, filename, as_attachment=True)


@report_bp.route("/reports", methods=["GET"])
@login_required
def report_history():
    reports = list_reports_for_user(session["user_id"])
    return success_response(reports)
