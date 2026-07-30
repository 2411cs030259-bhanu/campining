"""
database.py
MySQL connection management using a connection pool.

This module is the single place that knows how to talk to MySQL.
Routes and services never import mysql.connector directly - they go
through get_db_connection() / get_db_cursor() so the underlying driver
or database engine can be swapped later without touching business logic.
"""

import logging
from contextlib import contextmanager

import mysql.connector
from mysql.connector import pooling, Error as MySQLError

from config import get_config

logger = logging.getLogger(__name__)

config = get_config()

_pool = None


def init_db_pool():
    """
    Initialize the MySQL connection pool.
    Called once when the Flask application starts.
    """
    global _pool

    if _pool is not None:
        return _pool

    try:
        _pool = pooling.MySQLConnectionPool(
            pool_name="marketing_analytics_pool",
            pool_size=3,
            pool_reset_session=True,
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            autocommit=False,
            connection_timeout=10,
        )

        logger.info("MySQL connection pool initialized.")

    except MySQLError as err:
        logger.error("Failed to initialize MySQL connection pool: %s", err)
        raise

    return _pool


@contextmanager
def get_db_connection():
    """
    Get a MySQL connection from the pool.

    Automatically reconnects if Render/MySQL closed an idle connection.
    """

    global _pool

    if _pool is None:
        init_db_pool()

    conn = None

    try:
        conn = _pool.get_connection()

        # Handle stale connections after Render sleep/wakeup
        if not conn.is_connected():
            conn.reconnect(attempts=3, delay=2)

        yield conn

    except MySQLError as err:
        logger.error("Database connection error: %s", err)
        raise

    finally:
        if conn:
            conn.close()  # returns connection back to pool


@contextmanager
def get_db_cursor(commit: bool = False, dictionary: bool = True):
    """
    Context manager that yields a cursor and handles commit/rollback.

    Usage:

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "INSERT INTO users (...) VALUES (...)",
                values
            )
    """

    with get_db_connection() as conn:

        cursor = None

        try:
            cursor = conn.cursor(dictionary=dictionary)

            yield cursor

            if commit:
                conn.commit()

        except MySQLError as err:
            conn.rollback()
            logger.error("Database query failed: %s", err)
            raise

        finally:
            if cursor:
                cursor.close()


def test_connection() -> bool:
    """
    Simple database health check used by /api/v1/health.
    """

    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return True

    except MySQLError as err:
        logger.error("Database health check failed: %s", err)
        return False