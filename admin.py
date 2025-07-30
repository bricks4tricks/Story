from flask import Blueprint, request, jsonify
import traceback
from db_utils import get_db_connection, release_db_connection
from extensions import bcrypt

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/all-users', methods=['GET'])
def get_all_users():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT u.ID, u.Username, u.Email, u.UserType, u.CreatedOn,
                   p.Username AS parentusername
            FROM tbl_User u
            LEFT JOIN tbl_User p ON u.ParentUserID = p.ID
            ORDER BY u.ID;
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
