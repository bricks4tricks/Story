from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta, timezone
import secrets
import traceback
import os
import smtplib
from version_cache import update_users_version
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from extensions import bcrypt
from utils import validate_password, validate_email
from db_utils import (
    ensure_plan_column,
    get_db_connection,
    release_db_connection,
    ensure_user_preferences_table,
)
from auth_utils import SessionManager

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

SMTP_SERVER = os.environ.get('SMTP_SERVER')
port_value = os.environ.get("SMTP_PORT")
try:
    SMTP_PORT = int(port_value) if port_value else None
except (TypeError, ValueError):
    SMTP_PORT = None
SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL', 'https://logicandstories.com')
RESET_PASSWORD_EMAIL_TEMPLATE_HTML = """<html><body><a href='{{RESET_LINK}}'>Reset</a></body></html>"""


def send_email(receiver_email, subject, html_content):
    sender_email = SENDER_EMAIL or SMTP_USERNAME
    if not sender_email:
        print("Sender email is missing or empty. Email not sent.")
        return False
    if not all([SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, sender_email]):
        print("SMTP configuration incomplete. Email not sent.")
        return False
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
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
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
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
    cursor = None
    try:
        conn = get_db_connection()
        ensure_plan_column(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tbl_user WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Username or email already exists"}), 409
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        plan_to_insert = plan if plan else 'Monthly'
        cursor.execute(
            "INSERT INTO tbl_user (username, email, passwordhash, usertype, plan) VALUES (%s, %s, %s, 'Parent', %s) RETURNING id",
            (username, email, hashed_password, plan_to_insert)
        )
        new_user_id = cursor.fetchone()[0]
        # Create an associated subscription row if a plan was chosen
        if plan:
            if plan == 'Monthly':
                expires_on = datetime.now(timezone.utc) + timedelta(days=30)
            else:
                expires_on = datetime.now(timezone.utc) + timedelta(days=365)
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
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@auth_bp.route('/update-profile', methods=['POST', 'OPTIONS'])
def update_profile():
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    user_id = data.get('userId')
    username = data.get('username')
    email = data.get('email')
    if user_id is None or not username or not email:
        return jsonify({"status": "error", "message": "Missing fields"}), 400
    is_valid_email, email_msg = validate_email(email)
    if not is_valid_email:
        return jsonify({"status": "error", "message": email_msg}), 400
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT usertype FROM tbl_user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        if user[0] == 'Student':
            return jsonify({"status": "error", "message": "Students cannot update profile"}), 403
        cursor.execute(
            "SELECT id FROM tbl_user WHERE (username = %s OR email = %s) AND id != %s",
            (username, email, user_id),
        )
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "username or email is already in use by another account."}), 409
        cursor.execute(
            "UPDATE tbl_user SET username = %s, email = %s WHERE id = %s",
            (username, email, user_id),
        )
        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({"status": "error", "message": "User not found or no changes made."}), 404
        conn.commit()
        update_users_version()
        return jsonify({"status": "success", "message": "Profile updated successfully!"}), 200
    except Exception as e:
        print(f"Update Profile API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@auth_bp.route('/change-password', methods=['POST', 'OPTIONS'])
def change_password():
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    user_id = data.get('userId')
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
    if user_id is None or not current_password or not new_password:
        return jsonify({"status": "error", "message": "Missing fields"}), 400
    is_valid, message = validate_password(new_password)
    if not is_valid:
        return jsonify({"status": "error", "message": message}), 400
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT passwordhash, usertype FROM tbl_user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        stored_hash, user_type = user
        if user_type == 'Student':
            return jsonify({"status": "error", "message": "Students cannot change password"}), 403
        if not bcrypt.check_password_hash(stored_hash, current_password):
            return jsonify({"status": "error", "message": "Current password is incorrect"}), 401
        new_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        cursor.execute(
            "UPDATE tbl_user SET passwordhash = %s WHERE id = %s",
            (new_hash, user_id),
        )
        conn.commit()
        update_users_version()
        return jsonify({"status": "success", "message": "Password updated successfully."}), 200
    except Exception as e:
        print(f"Change Password API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@auth_bp.route('/preferences/<int:user_id>', methods=['GET', 'OPTIONS'])
def get_preferences(user_id):
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        ensure_user_preferences_table(conn)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT darkmode, fontsize FROM tbl_userpreferences WHERE user_id = %s",
            (user_id,),
        )
        prefs = cursor.fetchone()
        if prefs:
            darkmode, fontsize = prefs
        else:
            darkmode, fontsize = False, 'medium'
        return (
            jsonify({
                "status": "success",
                "darkMode": darkmode,
                "fontSize": fontsize,
            }),
            200,
        )
    except Exception as e:
        print(f"Get Preferences API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Could not retrieve preferences"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@auth_bp.route('/preferences', methods=['POST', 'OPTIONS'])
def save_preferences():
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    user_id = data.get('userId')
    dark_mode = data.get('darkMode')
    font_size = data.get('fontSize')
    if user_id is None or font_size is None:
        return jsonify({"status": "error", "message": "Missing fields"}), 400
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        ensure_user_preferences_table(conn)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tbl_userpreferences (user_id, darkmode, fontsize)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET darkmode = EXCLUDED.darkmode,
                fontsize = EXCLUDED.fontsize
            """,
            (user_id, dark_mode, font_size),
        )
        conn.commit()
        return jsonify({"status": "success", "message": "Preferences saved."}), 200
    except Exception as e:
        print(f"Save Preferences API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Could not save preferences"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@auth_bp.route('/select-plan', methods=['POST', 'OPTIONS'])
def select_plan():
    """Update a user's subscription plan after signup."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    # ``get_json`` returns ``None`` when the request body is empty or invalid JSON.
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    user_id = data.get('userId')
    plan = data.get('plan')
    # ``user_id`` may legitimately be ``0`` which is falsy, so check explicitly for ``None``
    if user_id is None or plan is None:
        return jsonify({"status": "error", "message": "Missing fields"}), 400
    allowed_plans = {'Monthly', 'Annual', 'Family'}
    if plan not in allowed_plans:
        return jsonify({"status": "error", "message": "Invalid plan selected"}), 400
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        ensure_plan_column(conn)
        cursor = conn.cursor()
        cursor.execute("UPDATE tbl_user SET plan = %s WHERE id = %s", (plan, user_id))
        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({"status": "error", "message": "User not found"}), 404
        if plan == 'Monthly':
            expires_on = datetime.now(timezone.utc) + timedelta(days=30)
        else:
            expires_on = datetime.now(timezone.utc) + timedelta(days=365)
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
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@auth_bp.route('/signin', methods=['POST', 'OPTIONS'])
def signin_user():
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"status": "error", "message": "Missing JSON body"}), 400
    username, password = data.get('username'), data.get('password')
    username = username.strip() if isinstance(username, str) else ''
    password = password.strip() if isinstance(password, str) else ''
    if not username or not password:
        return jsonify({"status": "error", "message": "Missing fields"}), 400
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, passwordhash, usertype, parentuserid FROM tbl_user WHERE username = %s",
            (username,),
        )
        user = cursor.fetchone()
        if user and bcrypt.check_password_hash(user[2], password):
            days_left = None
            # Check subscription status for non-admin users
            if user[3] != 'Admin':
                now_utc = datetime.now(timezone.utc)
                # Determine whose subscription to check: parent for students, self for parents
                if user[3] == 'Student':
                    parent_id = user[4]
                    if not parent_id:
                        return jsonify({
                            "status": "error",
                            "message": "Subscription inactive. Please renew to access your account.",
                        }), 403
                    cursor.execute(
                        "SELECT active, expires_on FROM tbl_subscription WHERE user_id = %s",
                        (parent_id,),
                    )
                    sub = cursor.fetchone()
                    if not sub:
                        return jsonify({
                            "status": "error",
                            "message": "Subscription inactive. Please renew to access your account.",
                        }), 403
                    active, expires_on = sub
                    if expires_on and expires_on.tzinfo is None:
                        expires_on = expires_on.replace(tzinfo=timezone.utc)
                    if expires_on and expires_on <= now_utc:
                        cursor.execute(
                            "UPDATE tbl_subscription SET active = FALSE WHERE user_id = %s",
                            (parent_id,),
                        )
                        conn.commit()
                        active = False
                    if not active:
                        return jsonify({
                            "status": "error",
                            "message": "Subscription inactive. Please renew to access your account.",
                        }), 403
                    days_left = (
                        (expires_on - now_utc).days
                        if expires_on and expires_on > now_utc
                        else None
                    )
                else:
                    cursor.execute(
                        "SELECT active, expires_on FROM tbl_subscription WHERE user_id = %s",
                        (user[0],),
                    )
                    sub = cursor.fetchone()
                    if sub:
                        active, expires_on = sub
                        if expires_on and expires_on.tzinfo is None:
                            expires_on = expires_on.replace(tzinfo=timezone.utc)
                        if expires_on and expires_on <= now_utc:
                            cursor.execute(
                                "UPDATE tbl_subscription SET active = FALSE WHERE user_id = %s",
                                (user[0],),
                            )
                            conn.commit()
                        days_left = (
                            (expires_on - now_utc).days
                            if expires_on and expires_on > now_utc
                            else None
                        )
            # Create session token
            session_token = SessionManager.create_session(user[0], user[3].lower())
            
            # Store token in httpOnly session cookie
            session['session_token'] = session_token
            session['user_id'] = user[0]
            session['user_type'] = user[3].lower()
            
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
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@auth_bp.route('/admin-signin', methods=['POST', 'OPTIONS'])
def admin_signin():
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"status": "error", "message": "Invalid username or password"}), 400
    username, password = username.strip(), password.strip()
    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, passwordhash, usertype FROM tbl_user WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        if user and bcrypt.check_password_hash(user[2], password) and user[3] == 'Admin':
            # Create session token like regular signin
            session_token = SessionManager.create_session(user[0], user[3].lower())
            
            # Store token in httpOnly session cookie
            session['session_token'] = session_token
            session['user_id'] = user[0]
            session['user_type'] = user[3].lower()
            
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
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@auth_bp.route('/forgot-password', methods=['POST', 'OPTIONS'])
def forgot_password():
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tbl_user WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            token, expiry = secrets.token_hex(32), datetime.now(timezone.utc) + timedelta(hours=1)
            cursor.execute(
                "UPDATE tbl_user SET resettoken = %s, resettokenexpiry = %s WHERE id = %s",
                (token, expiry, user[0]),
            )
            reset_link = f"{FRONTEND_BASE_URL}/reset-password.html?token={token}"
            email_content = RESET_PASSWORD_EMAIL_TEMPLATE_HTML.replace('{{RESET_LINK}}', reset_link)
            if not send_email(
                email, "Logic and Stories - Password Reset", email_content
            ):
                conn.rollback()
                return jsonify({"status": "error", "message": "Failed to send password reset email."}), 500
            conn.commit()
        return jsonify({"status": "success", "message": "If an account exists, a password reset link has been sent to your email."}), 200
    except Exception as e:
        print(f"Forgot Password API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@auth_bp.route('/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    token, new_password = data.get('token'), data.get('newPassword')
    if not all([token, new_password]):
        return jsonify({"status": "error", "message": "Token and new password are required."}), 400
    is_valid, message = validate_password(new_password)
    if not is_valid:
        return jsonify({"status": "error", "message": message}), 400
    conn = None
    cursor = None
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
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@auth_bp.route('/preferences/current', methods=['GET', 'OPTIONS'])
def get_current_user_preferences():
    """Get preferences for the currently authenticated user."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    # Get user ID from session
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        ensure_user_preferences_table(conn)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT darkmode, fontsize FROM tbl_userpreferences WHERE user_id = %s",
            (user_id,),
        )
        prefs = cursor.fetchone()
        if prefs:
            darkmode, fontsize = prefs
        else:
            darkmode, fontsize = False, 'medium'
        return (
            jsonify({
                "status": "success",
                "darkMode": darkmode,
                "fontSize": fontsize,
            }),
            200,
        )
    except Exception as e:
        print(f"Get Current User Preferences API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Could not retrieve preferences"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@auth_bp.route('/logout', methods=['POST', 'OPTIONS'])
def logout():
    """Logout and destroy session."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    # Get session token and destroy it
    session_token = session.get('session_token')
    if session_token:
        SessionManager.destroy_session(session_token)
    
    # Clear session
    session.clear()
    
    return jsonify({"status": "success", "message": "Logged out successfully"}), 200
