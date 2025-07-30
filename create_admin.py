import sys
import psycopg2
from flask_bcrypt import Bcrypt
import os
import traceback
import logging
from db_utils import db_cursor
# Database settings are read from environment variables in db_utils

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)

# --- SET YOUR ADMIN CREDENTIALS HERE ---
admin_username = 'admin'
admin_email = 'admin@logicandstories.com'
# Use an environment variable for the admin password, with a strong default for initial setup
admin_password = os.environ.get('ADMIN_PASSWORD', '9j*kX%NK^8snHd3aW8US') 

# --- SCRIPT LOGIC ---
bcrypt = Bcrypt()

logger.info("--- Admin Creation Script ---")
try:
    with db_cursor() as cursor:
        logger.info("Connected to database.")

        # Check if admin already exists
        cursor.execute("SELECT ID FROM tbl_User WHERE Username = %s OR Email = %s", (admin_username, admin_email))
        if cursor.fetchone():
            logger.error("An admin with username '%s' or email '%s' already exists.", admin_username, admin_email)
            sys.exit(1)

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
        logger.info("Password hashed successfully.")

        # Insert the new admin user
        cursor.execute(
            "INSERT INTO tbl_User (Username, Email, PasswordHash, UserType) VALUES (%s, %s, %s, 'Admin')",
            (admin_username, admin_email, hashed_password)
        )
        logger.info("SUCCESS! Admin user '%s' created.", admin_username)
        logger.info("You can now log in using the Admin Login page.")

except psycopg2.Error as err:
    logger.exception("DATABASE ERROR: %s", err)
except Exception as e:
    logger.exception("An unexpected error occurred: %s", e)
