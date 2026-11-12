from flask import Blueprint, request, jsonify, session
from auth.auth import role_required, hash_password
from database.db import get_connection

bp = Blueprint("user_routes", __name__, url_prefix="/api/users")


@bp.route("", methods=["GET"])
@role_required("admin")
def list_users():
    conn = get_connection()
    rows = conn.execute("SELECT id, username, full_name, role, created_at FROM users ORDER BY id").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@bp.route("", methods=["POST"])
@role_required("admin")
def create_user():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "").strip()
    role = data.get("role") or "officer"

    if not username or not password or not full_name:
        return jsonify({"error": "username, password and full_name are required."}), 400
    if role not in ("admin", "officer"):
        return jsonify({"error": "role must be 'admin' or 'officer'."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    conn = get_connection()
    existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "Username already exists."}), 400

    conn.execute(
        "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
        (username, hash_password(password), full_name, role),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "User created successfully."}), 201


@bp.route("/<int:user_id>", methods=["DELETE"])
@role_required("admin")
def delete_user(user_id):
    if user_id == session.get("user_id"):
        return jsonify({"error": "You cannot delete your own account while logged in."}), 400
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "User deleted."})
