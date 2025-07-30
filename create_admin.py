import psycopg2
from flask_bcrypt import Bcrypt
import os # Import os for environment variables

# --- CONFIGURATION ---
db_config = {
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'Dragon@123'),
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'port': os.environ.get('DB_PORT', '5432'),
    'database': os.environ.get('DB_NAME', 'educational_platform_db')
}

# --- SET YOUR ADMIN CREDENTIALS HERE ---
admin_username = 'admin'
admin_email = 'admin@logicandstories.com'
# Use an environment variable for the admin password, with a strong default for initial setup
admin_password = os.environ.get('ADMIN_PASSWORD', '9j*kX%NK^8snHd3aW8US') 

# --- SCRIPT LOGIC ---
bcrypt = Bcrypt()

print("--- Admin Creation Script ---")
try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    print("Connected to database.")

    # Check if admin already exists
    cursor.execute("SELECT ID FROM tbl_User WHERE Username = %s OR Email = %s", (admin_username, admin_email))
    if cursor.fetchone():
        print(f"Error: An admin with username '{admin_username}' or email '{admin_email}' already exists.")
    else:
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
        print("Password hashed successfully.")

        # Insert the new admin user
        cursor.execute(
            "INSERT INTO tbl_User (Username, Email, PasswordHash, UserType) VALUES (%s, %s, %s, 'Admin')",
            (admin_username, admin_email, hashed_password)
        )
        conn.commit()
        print(f"\nSUCCESS! Admin user '{admin_username}' created.")
        print("You can now log in using the Admin Login page.")

except psycopg2.Error as err:
    print(f"DATABASE ERROR: {err}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    if 'conn' in locals() and conn.closed == 0:
        cursor.close()
        conn.close()
        print("Database connection closed.")
