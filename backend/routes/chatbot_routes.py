"""
routes/chatbot_routes.py
Thin HTTP layer over the rule-based chatbot service.
"""

from flask import Blueprint, request

from utils.auth_decorators import login_required
from utils.response_helpers import success_response, error_response
from services.chatbot_service import get_answer

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/chatbot", methods=["POST"])
@login_required
def chatbot():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "")

    if not question.strip():
        return error_response("Please include a question.", 400)

    answer = get_answer(question)
    return success_response({"question": question, "answer": answer})
