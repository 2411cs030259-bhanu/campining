"""
app.py
Application factory and entry point for the Marketing Analytics
Platform backend.

Run locally with:
    python app.py

In production, use a WSGI server (e.g. gunicorn app:app).
"""

import logging

from flask import Flask
from flask_cors import CORS

from config import get_config
from database import init_db_pool, test_connection
from utils.response_helpers import error_response

from routes.auth_routes import auth_bp
from routes.upload_routes import upload_bp
from routes.report_routes import report_bp
from routes.chatbot_routes import chatbot_bp
from routes.analytics_routes import analytics_bp


def create_app():
    app = Flask(__name__)
    config = get_config()
    app.config.from_object(config)

    logging.basicConfig(
        level=logging.DEBUG if config.DEBUG else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # CORS: only allow the configured frontend origin(s), with credentials
    # (cookies) enabled so session-based auth works across origins.
    CORS(app, supports_credentials=True, origins=config.ALLOWED_ORIGINS)

    # Initialize the MySQL connection pool once at startup.
    init_db_pool()

    # Register blueprints under a single versioned API prefix so future
    # versions can introduce /api/v2 without breaking Version 1.0 clients.
    app.register_blueprint(auth_bp, url_prefix="/api/v1")
    app.register_blueprint(upload_bp, url_prefix="/api/v1")
    app.register_blueprint(report_bp, url_prefix="/api/v1")
    app.register_blueprint(chatbot_bp, url_prefix="/api/v1")
    app.register_blueprint(analytics_bp, url_prefix="/api/v1")

    @app.route("/api/v1/health", methods=["GET"])
    def health():
        db_ok = test_connection()
        status = "ok" if db_ok else "degraded"
        return {"status": status, "database": "connected" if db_ok else "unavailable"}, (
            200 if db_ok else 503
        )

    # ---- Global error handlers: never leak raw tracebacks to the client ----
    @app.errorhandler(404)
    def not_found(e):
        return error_response("The requested resource was not found.", 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error_response("This action is not allowed.", 405)

    @app.errorhandler(413)
    def too_large(e):
        return error_response("The uploaded file is too large.", 413)

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.exception("Unhandled server error")
        return error_response("Something went wrong on our end. Please try again.", 500)

    return app


app = create_app()

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
