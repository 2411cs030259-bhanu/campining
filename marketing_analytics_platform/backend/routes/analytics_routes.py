"""
routes/analytics_routes.py
Serves dashboard-level summary data, e.g. KPIs from the user's
most recently generated report, so the Dashboard page has
something to show without requiring a fresh upload every visit.
"""

from flask import Blueprint, session

from utils.auth_decorators import login_required
from utils.response_helpers import success_response
from services.report_service import list_reports_for_user

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/dashboard-summary", methods=["GET"])
@login_required
def dashboard_summary():
    reports = list_reports_for_user(session["user_id"])
    latest = reports[0] if reports else None
    return success_response({
        "latest_report": latest,
        "total_reports": len(reports),
    })
