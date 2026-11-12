"""
AI assistant route — talks to Gemini on behalf of the frontend widget.
New file; does not modify any existing route file.
"""
from flask import Blueprint, request, jsonify

from auth.auth import login_required
from ai.gemini_client import ask_gemini, GeminiError

bp = Blueprint("ai_routes", __name__, url_prefix="/api/ai")


@bp.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not message:
        return jsonify({"error": "message is required."}), 400
    if len(history) > 20:
        history = history[-20:]

    try:
        reply = ask_gemini(message, history)
    except GeminiError as e:
        return jsonify({"error": str(e)}), 502

    return jsonify({"reply": reply})
