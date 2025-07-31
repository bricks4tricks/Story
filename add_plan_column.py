import psycopg2
from db_utils import db_cursor

"""Utility script to add the ``plan`` column to ``tbl_user`` if it does not exist."""

with db_cursor() as cursor:
    cursor.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'tbl_user' AND column_name = 'plan'
        """
    )
    if cursor.fetchone():
        print("'plan' column already exists. No changes made.")
    else:
        cursor.execute("ALTER TABLE tbl_user ADD COLUMN plan VARCHAR(20) DEFAULT 'Monthly'")
        print("Added 'plan' column to tbl_user with default 'Monthly'.")
