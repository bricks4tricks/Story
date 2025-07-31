from flask import Blueprint, request, jsonify
import traceback
from version_cache import users_version
from db_utils import get_db_connection, release_db_connection


admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route("/users-version", methods=["GET"])
def get_users_version():
    return jsonify({"version": users_version.isoformat()})

@admin_bp.route('/all-users', methods=['GET'])
def get_all_users():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
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
    finally:
        if conn:
            release_db_connection(conn)
