import os
import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool
import traceback
from contextlib import contextmanager
from dotenv import load_dotenv, find_dotenv

# Load variables from a .env file if present. This allows developers to
# configure database credentials without hardcoding them in the source.
# ``find_dotenv`` searches parent directories to locate the file, ensuring
# it is loaded even when the application is executed from another path.
load_dotenv(find_dotenv())


def _load_db_config():
    """Return DB connection settings loaded from environment variables.

    The function supports either a full ``DATABASE_URL`` connection string or
    the individual ``DB_*`` variables. ``DATABASE_URL`` is commonly provided by
    hosting platforms like Render. If none of the required variables are
    present, a ``RuntimeError`` is raised to make the misconfiguration obvious.
    """

    dsn = os.environ.get("DATABASE_URL")
    if dsn:
        # Ensure SSL is used when connecting to managed databases unless the URL
        # already specifies ``sslmode``.
        if "sslmode" not in dsn:
            connector = "&" if "?" in dsn else "?"
            dsn += f"{connector}sslmode=require"
        return {"dsn": dsn}

    required = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]
    config = {}
    missing = []
    for var in required:
        value = os.environ.get(var)
        if not value:
            missing.append(var)
        config[var] = value

    if missing:
        raise RuntimeError(
            f"Missing required database environment variables: {', '.join(missing)}"
        )

    return {
        "user": config["DB_USER"],
        "password": config["DB_PASSWORD"],
        "host": config["DB_HOST"],
        "port": config["DB_PORT"],
        "database": config["DB_NAME"],
    }


# Centralized database configuration loaded once at import time
db_config = _load_db_config()

# Global connection pool. Initialized lazily on first connection request.
connection_pool = None


def _get_pool():
    """Lazily create and return a global connection pool."""
    global connection_pool
    if connection_pool is None:
        try:
            pool_kwargs = {
                "keepalives": 1,
                "keepalives_idle": 60,
                "keepalives_interval": 30,
                "keepalives_count": 5,
            }
            if "dsn" in db_config:
                connection_pool = SimpleConnectionPool(
                    1, 10, db_config["dsn"], **pool_kwargs
                )
            else:
                connection_pool = SimpleConnectionPool(
                    1, 10, **db_config, **pool_kwargs
                )
        except Exception as e:
            print(f"Database connection pool creation error: {e}")
            traceback.print_exc()
            raise
    return connection_pool


def get_db_connection():
    """Obtain a database connection from the global pool."""
    try:
        pool = _get_pool()
        return pool.getconn()
    except Exception as e:
        print(f"Database connection error: {e}")
        traceback.print_exc()
        raise


def release_db_connection(conn):
    """Return a connection to the pool or close it if no pool is available."""
    try:
        if connection_pool:
            connection_pool.putconn(conn)
        else:
            conn.close()
    except Exception as e:
        print(f"Error releasing connection: {e}")
        traceback.print_exc()


@contextmanager
def db_connection():
    """Provide a context manager for a database connection."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        release_db_connection(conn)


@contextmanager
def db_cursor(dictionary=False):
    """Yield a cursor with automatic commit/rollback and cleanup."""
    with db_connection() as conn:
        if dictionary:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()

