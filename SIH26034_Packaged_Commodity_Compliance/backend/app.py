"""
SIH26034 — Packaged Commodity Compliance
Main Flask application entry point.

Run with:  python app.py
Creates/initializes the SQLite database automatically on first run.
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS

import config
from database.db import init_db
from api import routes_auth, routes_scan, routes_dashboard, routes_history, routes_users, routes_ai


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Allow the Vite dev server to call the API with cookies for session auth
    CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

    app.register_blueprint(routes_auth.bp)
    app.register_blueprint(routes_scan.bp)
    app.register_blueprint(routes_dashboard.bp)
    app.register_blueprint(routes_history.bp)
    app.register_blueprint(routes_users.bp)
    app.register_blueprint(routes_ai.bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "SIH26034 Compliance Backend"})

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": "Uploaded file is too large."}), 413

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "An unexpected server error occurred. Please try again."}), 500

    return app


if __name__ == "__main__":
    init_db()
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"\nSIH26034 Compliance backend running at http://localhost:{port}")
    print("Database initialized at backend/compliance.db\n")
    app.run(host="0.0.0.0", port=port, debug=True)
