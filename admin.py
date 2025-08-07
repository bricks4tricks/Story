from flask import Blueprint, request, jsonify
import os
import traceback
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
import version_cache
from db_utils import db_cursor
from seed_database import seed_data


admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route("/users-version", methods=["GET"])
def get_users_version():
    return jsonify({"version": version_cache.users_version.isoformat()})

@admin_bp.route('/all-users', methods=['GET'])
def get_all_users():
    try:
        with db_cursor() as cursor:
            query = """
                SELECT u.id, u.username, u.email, u.usertype, u.createdon,
                       p.username AS parentusername,
                       s.active, s.expires_on
                FROM tbl_user u
                LEFT JOIN tbl_user p ON u.parentuserid = p.id
                LEFT JOIN tbl_subscription s ON u.id = s.user_id
                ORDER BY u.id;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            users = []
            now = datetime.now(timezone.utc)
            for row in rows:
                expires_on = row[7]
                if expires_on and expires_on.tzinfo is None:
                    expires_on = expires_on.replace(tzinfo=timezone.utc)
                days_left = (
                    (expires_on - now).days if expires_on and row[6] else None
                )
                users.append({
                    'ID': row[0],
                    'Username': row[1],
                    'Email': row[2],
                    'UserType': row[3],
                    'CreatedOn': row[4],
                    'ParentUsername': row[5],
                    'SubscriptionDaysLeft': days_left,
                })
            return jsonify(users)
    except Exception as e:
        print(f"Get All Users API Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal error"}), 500


@admin_bp.route('/seed-database', methods=['POST'])
def seed_database_upload():
    tmp_path = None
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"message": "No file uploaded"}), 400
        tmp_path = os.path.join('/tmp', secure_filename(file.filename))
        file.save(tmp_path)
        seed_data(csv_file_name=tmp_path)
        return jsonify({"message": "Database seeded successfully"})
    except Exception as e:
        print(f"Seed Database API Error: {e}")
        traceback.print_exc()
        return jsonify({"message": "Internal error"}), 500
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
