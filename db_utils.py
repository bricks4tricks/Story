import os
import psycopg2
import traceback
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


def get_db_connection():
    """Return a new database connection with error logging."""
    try:
        if "dsn" in db_config:
            return psycopg2.connect(db_config["dsn"])
        return psycopg2.connect(**db_config)
    except Exception as e:
        print(f"Database connection error: {e}")
        traceback.print_exc()
        raise
