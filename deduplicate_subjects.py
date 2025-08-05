"""Maintenance script to remove duplicate subject names from ``tbl_subject``."""

from db_utils import db_cursor


with db_cursor() as cursor:
    cursor.execute(
        """
        DELETE FROM tbl_subject a
        USING tbl_subject b
        WHERE a.id < b.id AND LOWER(TRIM(a.subjectname)) = LOWER(TRIM(b.subjectname));
        """
    )
    print("Removed duplicate subjects from tbl_subject.")

