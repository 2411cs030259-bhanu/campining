"""
config.py
Centralized application configuration.

All secrets and environment-specific values are read from environment
variables (loaded from a .env file in development via python-dotenv).
Nothing here is hardcoded, so this file is safe to commit.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


class Config:
    """Base configuration shared by all environments."""

    # --- Flask / security ---
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = ENV == "development"

    # --- Session ---
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _get_bool("SESSION_COOKIE_SECURE", default=(ENV == "production"))
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # --- Database (MySQL) ---
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_NAME = os.getenv("DB_NAME", "marketing_analytics")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    # --- CORS ---
    ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]

    # --- Uploads ---
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    REPORT_FOLDER = os.getenv("REPORT_FOLDER", "reports")
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10")) * 1024 * 1024
    ALLOWED_UPLOAD_EXTENSIONS = {"csv"}

    # Columns required in an uploaded campaign dataset
    REQUIRED_UPLOAD_COLUMNS = [
        "campaign",
        "platform",
        "impressions",
        "clicks",
        "ad_spend",
        "conversions",
        "revenue",
    ]


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DB_NAME = os.getenv("TEST_DB_NAME", "marketing_analytics_test")


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return CONFIG_MAP.get(env, DevelopmentConfig)
