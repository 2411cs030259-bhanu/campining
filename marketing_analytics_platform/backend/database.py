"""
database.py
MySQL connection management using a connection pool.

This module is the single place that knows how to talk to MySQL.
Routes and services never import mysql.connector directly - they go
through get_db_connection() / run_query() so the underlying driver
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
    """Initialize the MySQL connection pool. Call once at app startup."""
    global _pool
    if _pool is not None:
        return _pool

    try:
        _pool = pooling.MySQLConnectionPool(
            pool_name="marketing_analytics_pool",
            pool_size=5,
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            autocommit=False,
        )
        logger.info("MySQL connection pool initialized.")
    except MySQLError as err:
        logger.error("Failed to initialize MySQL connection pool: %s", err)
        raise
    return _pool


@contextmanager
def get_db_connection():
    """Context manager that yields a pooled MySQL connection."""
    global _pool
    if _pool is None:
        init_db_pool()
    conn = _pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()  # returns the connection to the pool


@contextmanager
def get_db_cursor(commit: bool = False, dictionary: bool = True):
    """
    Context manager that yields a cursor and handles commit/rollback.

    Usage:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO users ...", params)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=dictionary)
        try:
            yield cursor
            if commit:
                conn.commit()
        except MySQLError:
            conn.rollback()
            raise
        finally:
            cursor.close()


def test_connection() -> bool:
    """Simple health check used by /api/health."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return True
    except MySQLError as err:
        logger.error("Database health check failed: %s", err)
        return False
