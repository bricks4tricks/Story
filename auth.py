from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import secrets
import traceback
import os
import smtplib
from version_cache import update_users_version
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from extensions import bcrypt
from utils import validate_password, validate_email
from db_utils import ensure_plan_column

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = int(os.environ.get('SMTP_PORT') or 0) or None
SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL', 'https://logicandstories.com')
RESET_PASSWORD_EMAIL_TEMPLATE_HTML = """<html><body><a href='{{RESET_LINK}}'>Reset</a></body></html>"""


def send_email(receiver_email, subject, html_content):
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email to {receiver_email}: {e}")
        traceback.print_exc()
        return False


@auth_bp.route('/signup', methods=['POST', 'OPTIONS'])
def signup_user():
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    from app import get_db_connection, release_db_connection
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    plan = data.get('plan')  # optional during initial signup
    if not all([username, email, password]):
        return jsonify({"status": "error", "message": "Missing fields"}), 400
    is_valid_email, email_msg = validate_email(email)
    if not is_valid_email:
        return jsonify({"status": "error", "message": email_msg}), 400
    is_valid, message = validate_password(password)
    if not is_valid:
        return jsonify({"status": "error", "message": message}), 400
    allowed_plans = {'Monthly', 'Annual', 'Family'}
    if plan and plan not in allowed_plans:
        return jsonify({"status": "error", "message": "Invalid plan selected"}), 400
    conn = None
    try:
        conn = get_db_connection()
        ensure_plan_column(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tbl_user WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Username or email already exists"}), 409
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute(
            "INSERT INTO tbl_user (username, email, passwordhash, usertype, plan) VALUES (%s, %s, %s, 'Parent', %s) RETURNING id",
            (username, email, hashed_password, plan)
        )
        new_user_id = cursor.fetchone()[0]
        # Create an associated subscription row if a plan was chosen
        if plan:
            if plan == 'Monthly':
                expires_on = datetime.utcnow() + timedelta(days=30)
            else:
                expires_on = datetime.utcnow() + timedelta(days=365)
            cursor.execute(
                "INSERT INTO tbl_subscription (user_id, active, expires_on) VALUES (%s, TRUE, %s) ON CONFLICT (user_id) DO NOTHING",
                (new_user_id, expires_on)
            )
        conn.commit()
        update_users_version()
        return jsonify({"status": "success", "message": "Parent account created successfully!", "userId": new_user_id}), 201
    except Exception as e:
        print(f"Signup API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@auth_bp.route('/select-plan', methods=['POST', 'OPTIONS'])
def select_plan():
    """Update a user's subscription plan after signup."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    from app import get_db_connection, release_db_connection
    data = request.get_json()
    user_id = data.get('userId')
    plan = data.get('plan')
    if not all([user_id, plan]):
        return jsonify({"status": "error", "message": "Missing fields"}), 400
    allowed_plans = {'Monthly', 'Annual', 'Family'}
    if plan not in allowed_plans:
        return jsonify({"status": "error", "message": "Invalid plan selected"}), 400
    conn = None
    try:
        conn = get_db_connection()
        ensure_plan_column(conn)
        cursor = conn.cursor()
        cursor.execute("UPDATE tbl_user SET plan = %s WHERE id = %s", (plan, user_id))
        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "User not found"}), 404
        if plan == 'Monthly':
            expires_on = datetime.utcnow() + timedelta(days=30)
        else:
            expires_on = datetime.utcnow() + timedelta(days=365)
        cursor.execute(
            "INSERT INTO tbl_subscription (user_id, active, expires_on) VALUES (%s, TRUE, %s) "
            "ON CONFLICT (user_id) DO UPDATE SET active = TRUE, expires_on = EXCLUDED.expires_on",
            (user_id, expires_on)
        )
        conn.commit()
        update_users_version()
        return jsonify({"status": "success", "message": "Plan updated"}), 200
    except Exception as e:
        print(f"Select Plan API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@auth_bp.route('/signin', methods=['POST', 'OPTIONS'])
def signin_user():
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    from app import get_db_connection, release_db_connection
    data = request.get_json()
    username, password = data.get('username'), data.get('password')
    if not all([username, password]):
        return jsonify({"status": "error", "message": "Missing fields"}), 400
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, passwordhash, usertype FROM tbl_user WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        if user and bcrypt.check_password_hash(user[2], password):
            days_left = None
            # Check subscription status for non-admin users
            if user[3] != 'Admin':
                cursor.execute(
                    "SELECT active, expires_on FROM tbl_subscription WHERE user_id = %s",
                    (user[0],),
                )
                sub = cursor.fetchone()
                if sub:
                    active, expires_on = sub
                    if expires_on and expires_on <= datetime.utcnow():
                        cursor.execute(
                            "UPDATE tbl_subscription SET active = FALSE WHERE user_id = %s",
                            (user[0],),
                        )
                        conn.commit()
                        active = False
                    if not active:
                        return jsonify({
                            "status": "error",
                            "message": "Subscription inactive. Please renew to access your account.",
                        }), 403
                    days_left = (expires_on - datetime.utcnow()).days if expires_on else None
            return jsonify({
                "status": "success",
                "message": "Login successful!",
                "user": {"id": user[0], "username": user[1], "userType": user[3]},
                "subscriptionDaysLeft": days_left if user[3] != 'Admin' else None,
            }), 200
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401
    except Exception as e:
        print(f"Signin API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@auth_bp.route('/admin-signin', methods=['POST', 'OPTIONS'])
def admin_signin():
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    from app import get_db_connection, release_db_connection
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, passwordhash, usertype FROM tbl_user WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        if user and bcrypt.check_password_hash(user[2], password) and user[3] == 'Admin':
            return jsonify({
                "status": "success",
                "message": "Admin login successful!",
                "user": {"id": user[0], "username": user[1], "userType": user[3]},
            }), 200
        return jsonify({"status": "error", "message": "Invalid credentials or not an admin"}), 401
    except Exception as e:
        print(f"Admin Signin API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@auth_bp.route('/forgot-password', methods=['POST', 'OPTIONS'])
def forgot_password():
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    from app import get_db_connection, release_db_connection
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tbl_user WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            token, expiry = secrets.token_hex(32), datetime.now() + timedelta(hours=1)
            cursor.execute("UPDATE tbl_user SET resettoken = %s, resettokenexpiry = %s WHERE id = %s", (token, expiry, user[0]))
            conn.commit()
            reset_link = f"{FRONTEND_BASE_URL}/reset-password.html?token={token}"
            email_content = RESET_PASSWORD_EMAIL_TEMPLATE_HTML.replace('{{RESET_LINK}}', reset_link)
            send_email(email, "Logic and Stories - Password Reset", email_content)
        return jsonify({"status": "success", "message": "If an account exists, a password reset link has been sent to your email."}), 200
    except Exception as e:
        print(f"Forgot Password API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)


@auth_bp.route('/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    from app import get_db_connection, release_db_connection
    data = request.get_json()
    token, new_password = data.get('token'), data.get('newPassword')
    if not all([token, new_password]):
        return jsonify({"status": "error", "message": "Token and new password are required."}), 400
    is_valid, message = validate_password(new_password)
    if not is_valid:
        return jsonify({"status": "error", "message": message}), 400
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tbl_user WHERE resettoken = %s AND resettokenexpiry > NOW()", (token,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"status": "error", "message": "Invalid or expired reset token."}), 400
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        cursor.execute(
            "UPDATE tbl_user SET passwordhash = %s, resettoken = NULL, resettokenexpiry = NULL WHERE id = %s",
            (hashed_password, user[0])
        )
        conn.commit()
        return jsonify({"status": "success", "message": "Password has been reset successfully."}), 200
    except Exception as e:
        print(f"Reset Password API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if conn:
            release_db_connection(conn)
