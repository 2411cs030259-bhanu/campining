"""
database.py
MySQL connection management using a connection pool.
Optimized for cloud platforms like Render.
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
    Called once when the application starts.
    """
    global _pool

    if _pool is not None:
        return _pool

    try:
        _pool = pooling.MySQLConnectionPool(
            pool_name="marketing_analytics_pool",
            pool_size=10,                    # Increased pool size
            pool_reset_session=True,

            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,

            autocommit=False,

            # Timeouts
            connection_timeout=10,
            read_timeout=15,
            write_timeout=15,
        )

        logger.info("MySQL connection pool initialized successfully.")

    except MySQLError as err:
        logger.exception("Unable to initialize MySQL connection pool.")
        raise

    return _pool


@contextmanager
def get_db_connection():
    """
    Returns a valid MySQL connection.

    If Render or MySQL closed the connection,
    automatically reconnect.
    """

    global _pool

    if _pool is None:
        init_db_pool()

    conn = None

    try:
        conn = _pool.get_connection()

        logger.debug("Database connection acquired.")

        try:
            conn.ping(reconnect=True, attempts=3, delay=2)
        except MySQLError:
            logger.warning("Lost database connection. Reconnecting...")
            conn.reconnect(attempts=3, delay=2)

        yield conn

    except MySQLError as err:
        logger.exception("Database connection failed.")
        raise

    finally:
        if conn:
            conn.close()
            logger.debug("Database connection returned to pool.")


@contextmanager
def get_db_cursor(commit=False, dictionary=True):
    """
    Provides a cursor with automatic commit / rollback.
    """

    with get_db_connection() as conn:

        cursor = None

        try:
            cursor = conn.cursor(dictionary=dictionary)

            yield cursor

            if commit:
                conn.commit()

        except MySQLError:
            conn.rollback()
            logger.exception("Database query failed.")
            raise

        finally:
            if cursor:
                cursor.close()


def test_connection():
    """
    Used by /health endpoint.
    """

    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return True

    except MySQLError:
        logger.exception("Database health check failed.")
        return False