import mysql.connector
from flask_bcrypt import Bcrypt

# --- CONFIGURATION ---
db_config = {
    'user': 'root',
    'password': 'Dragon@123',  # YOUR MYSQL PASSWORD HERE
    'host': '127.0.0.1',
    'database': 'educational_platform_db'
}

# --- SET YOUR ADMIN CREDENTIALS HERE ---
admin_username = 'admin'
admin_email = 'admin@logicandstories.com'
admin_password = '9j*kX%NK^8snHd3aW8US' # CHOOSE A STRONG PASSWORD

# --- SCRIPT LOGIC ---
bcrypt = Bcrypt()

print("--- Admin Creation Script ---")
try:
    conn = mysql.connector.connect(**db_config)
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

except mysql.connector.Error as err:
    print(f"DATABASE ERROR: {err}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print("Database connection closed.")