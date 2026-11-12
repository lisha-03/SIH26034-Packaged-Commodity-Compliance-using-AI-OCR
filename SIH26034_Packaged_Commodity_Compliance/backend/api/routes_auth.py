from flask import Blueprint, request, jsonify, session

from auth.auth import get_user_by_username, verify_password, get_user_by_id

bp = Blueprint("auth_routes", __name__, url_prefix="/api/auth")


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    user = get_user_by_username(username)
    if user is None or not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid username or password."}), 401

    session["user_id"] = user["id"]
    session["role"] = user["role"]
    session["full_name"] = user["full_name"]

    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
    })


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out."})


@bp.route("/me", methods=["GET"])
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401
    user = get_user_by_id(user_id)
    if user is None:
        session.clear()
        return jsonify({"error": "Not authenticated."}), 401
    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
    })
