import os
import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extensions import connection as PGConnection
import traceback
from contextlib import contextmanager
from typing import Generator, Dict
from dotenv import load_dotenv, find_dotenv

# Load variables from a .env file if present. This allows developers to
# configure database credentials without hardcoding them in the source.
# ``find_dotenv`` searches parent directories to locate the file, ensuring
# it is loaded even when the application is executed from another path.
load_dotenv(find_dotenv())


def _load_db_config() -> Dict[str, str]:
    """Load database connection settings optimized for Render PostgreSQL.

    This helper prioritizes DATABASE_URL (Render standard) and handles
    the postgres:// to postgresql:// conversion required by psycopg2.
    """
    from config import get_database_config
    return get_database_config()


# Centralized database configuration loaded once at import time
db_config = _load_db_config()

# Global connection pool. Initialized lazily on first connection request.
connection_pool = None


def _get_pool():
    """Lazily create and return a global connection pool optimized for Render."""
    global connection_pool
    if connection_pool is None:
        try:
            # Connection pool settings optimized for Render PostgreSQL
            pool_kwargs = {
                "keepalives": 1,
                "keepalives_idle": 60,
                "keepalives_interval": 30,
                "keepalives_count": 5,
            }
            
            # Extract pool settings
            pool_min = db_config.pop('pool_min', 2)
            pool_max = db_config.pop('pool_max', 20)
            
            if "dsn" in db_config:
                connection_pool = SimpleConnectionPool(
                    pool_min, pool_max, db_config["dsn"], **pool_kwargs
                )
            else:
                # Add sslmode for managed PostgreSQL if not present
                if 'sslmode' not in db_config:
                    db_config['sslmode'] = 'require'
                
                connection_pool = SimpleConnectionPool(
                    pool_min, pool_max, **db_config, **pool_kwargs
                )
        except Exception as e:
            error_msg = f"Failed to create database connection pool: {e}"
            print(error_msg)
            traceback.print_exc()
            raise RuntimeError(error_msg) from e
    return connection_pool


def get_db_connection() -> PGConnection:
    """Return a database connection from the global pool."""
    try:
        pool = _get_pool()
        return pool.getconn()
    except Exception as e:
        print(f"Database connection error: {e}")
        traceback.print_exc()
        raise


def release_db_connection(conn: PGConnection) -> None:
    """Return ``conn`` to the pool or close it if no pool exists."""
    try:
        if connection_pool:
            connection_pool.putconn(conn)
        else:
            conn.close()
    except Exception as e:
        print(f"Error releasing connection: {e}")
        traceback.print_exc()


@contextmanager
def db_connection() -> Generator[PGConnection, None, None]:
    """Yield a database connection with automatic commit or rollback."""
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


def ensure_plan_column(conn):
    """Ensure the ``plan`` column exists in ``tbl_user``."""
    cur = conn.cursor()
    try:
        cur.execute(
            "ALTER TABLE tbl_user ADD COLUMN IF NOT EXISTS plan VARCHAR(20) DEFAULT 'Monthly'"
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def ensure_user_preferences_table(conn):
    """Create ``tbl_userpreferences`` if it does not already exist."""
    cur = conn.cursor()
    try:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tbl_userpreferences (
                user_id INTEGER PRIMARY KEY REFERENCES tbl_user(id) ON DELETE CASCADE,
                darkmode BOOLEAN NOT NULL DEFAULT FALSE,
                fontsize VARCHAR(10) NOT NULL DEFAULT 'medium'
            )
            """
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def ensure_topicsubject_table(conn):
    """Create the ``tbl_topicsubject`` join table if it doesn't exist."""
    cur = conn.cursor()
    try:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tbl_topicsubject (
                topicid INTEGER REFERENCES tbl_topic(id) ON DELETE CASCADE,
                subjectid INTEGER REFERENCES tbl_subject(id) ON DELETE CASCADE,
                createdby VARCHAR(50),
                PRIMARY KEY (topicid, subjectid)
            )
            """
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()

