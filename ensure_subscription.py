from datetime import datetime, timedelta
from db_utils import db_cursor

"""Ensure the ``tbl_subscription`` table and rows for existing users exist.

This script will also add any missing columns and populate an ``expires_on``
timestamp based on the user's plan (Monthly => 30 days, others => 1 year).
"""

with db_cursor() as cursor:
    # Create table if it doesn't exist with all required columns
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tbl_subscription (
            user_id INTEGER PRIMARY KEY REFERENCES tbl_user(id),
            active BOOLEAN NOT NULL DEFAULT TRUE,
            expires_on TIMESTAMP,
            cancelled_on TIMESTAMP
        );
        """
    )
    # Add missing columns if running against an older schema
    cursor.execute(
        "ALTER TABLE tbl_subscription ADD COLUMN IF NOT EXISTS expires_on TIMESTAMP"
    )
    cursor.execute(
        "ALTER TABLE tbl_subscription ADD COLUMN IF NOT EXISTS cancelled_on TIMESTAMP"
    )

    # Ensure each user has a subscription row with an expiration date
    cursor.execute("SELECT id, plan FROM tbl_user")
    users = cursor.fetchall()
    for uid, plan in users:
        if plan == 'Monthly':
            expires = datetime.utcnow() + timedelta(days=30)
        else:
            expires = datetime.utcnow() + timedelta(days=365)
        cursor.execute(
            """
            INSERT INTO tbl_subscription (user_id, active, expires_on)
            VALUES (%s, TRUE, %s)
            ON CONFLICT (user_id) DO NOTHING;
            """,
            (uid, expires),
        )
print("Subscription table and rows ensured.")
