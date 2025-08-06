from flask import Blueprint, request, jsonify
import os
import traceback
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
                       p.username AS parentusername
                FROM tbl_user u
                LEFT JOIN tbl_user p ON u.parentuserid = p.id
                ORDER BY u.id;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            users = []
            for row in rows:
                users.append({
                    'ID': row[0],
                    'Username': row[1],
                    'Email': row[2],
                    'UserType': row[3],
                    'CreatedOn': row[4],
                    'ParentUsername': row[5]
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
