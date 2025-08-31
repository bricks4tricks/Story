"""
Subscription management blueprint for handling user subscriptions and plans.
Handles all subscription-related API endpoints.
"""

from flask import Blueprint, jsonify, request
import traceback
from auth_utils import require_auth, require_user_access
from db_utils import release_db_connection
# Make subscription.get_db_connection patchable via app.get_db_connection for tests
import app
def get_db_connection():
    return app.get_db_connection()
from datetime import datetime, timedelta, timezone

subscription_bp = Blueprint('subscription', __name__, url_prefix='/api')

# =================================================================
#  SUBSCRIPTION MANAGEMENT ENDPOINTS
# =================================================================

@subscription_bp.route('/subscription-status/<int:user_id>', methods=['GET', 'OPTIONS'])
def get_subscription_status(user_id):
    """Get subscription status for a user."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user's subscription info
        cursor.execute("""
            SELECT 
                s.plan_type,
                s.status,
                s.start_date,
                s.end_date,
                s.auto_renew,
                u.plan as user_plan
            FROM tbl_user u
            LEFT JOIN tbl_subscription s ON u.id = s.user_id
            WHERE u.id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        
        if not result:
            return jsonify(success=False, message="User not found"), 404
        
        subscription_data = {
            'user_id': user_id,
            'plan_type': result[0],
            'status': result[1],
            'start_date': result[2].isoformat() if result[2] else None,
            'end_date': result[3].isoformat() if result[3] else None,
            'auto_renew': result[4],
            'user_plan': result[5],
            'is_active': False,
            'days_remaining': 0
        }
        
        # Calculate if subscription is active and days remaining
        if result[1] == 'active' and result[3]:
            end_date = result[3]
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            now = datetime.now(timezone.utc)
            if end_date > now:
                subscription_data['is_active'] = True
                subscription_data['days_remaining'] = (end_date - now).days
        
        return jsonify(success=True, subscription=subscription_data)
        
    except Exception as e:
        print(f"Subscription Status API Error: {e}")
        return jsonify(success=False, message="Failed to fetch subscription status"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@subscription_bp.route('/cancel-subscription/<int:user_id>', methods=['POST', 'OPTIONS'])
def cancel_subscription(user_id):
    """Cancel a user's subscription."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user has an active subscription
        cursor.execute("""
            SELECT id, status FROM tbl_subscription 
            WHERE user_id = %s AND status = 'active'
        """, (user_id,))
        
        subscription = cursor.fetchone()
        if not subscription:
            return jsonify(success=False, message="No active subscription found"), 404
        
        # Update subscription status
        cursor.execute("""
            UPDATE tbl_subscription 
            SET status = 'cancelled', auto_renew = false, updated_at = NOW()
            WHERE user_id = %s
        """, (user_id,))
        
        # Update user plan to free
        cursor.execute("""
            UPDATE tbl_user 
            SET plan = 'free'
            WHERE id = %s
        """, (user_id,))
        
        conn.commit()
        
        return jsonify(success=True, message="Subscription cancelled successfully")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Cancel Subscription API Error: {e}")
        return jsonify(success=False, message="Failed to cancel subscription"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@subscription_bp.route('/renew-subscription/<int:user_id>', methods=['POST', 'OPTIONS'])
def renew_subscription(user_id):
    """Renew a user's subscription."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    data = request.get_json() or {}
    plan_type = data.get('plan_type', 'premium')
    duration_months = data.get('duration_months', 1)
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate new subscription dates
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=duration_months * 30)  # Approximate month calculation
        
        # Check if user has existing subscription
        cursor.execute("""
            SELECT id FROM tbl_subscription WHERE user_id = %s
        """, (user_id,))
        
        existing_subscription = cursor.fetchone()
        
        if existing_subscription:
            # Update existing subscription
            cursor.execute("""
                UPDATE tbl_subscription 
                SET plan_type = %s, status = 'active', start_date = %s, end_date = %s, 
                    auto_renew = true, updated_at = NOW()
                WHERE user_id = %s
            """, (plan_type, start_date, end_date, user_id))
        else:
            # Create new subscription
            cursor.execute("""
                INSERT INTO tbl_subscription 
                (user_id, plan_type, status, start_date, end_date, auto_renew, created_at)
                VALUES (%s, %s, 'active', %s, %s, true, NOW())
            """, (user_id, plan_type, start_date, end_date))
        
        # Update user plan
        cursor.execute("""
            UPDATE tbl_user 
            SET plan = %s
            WHERE id = %s
        """, (plan_type, user_id))
        
        conn.commit()
        
        return jsonify(
            success=True, 
            message="Subscription renewed successfully",
            end_date=end_date.isoformat()
        )
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Renew Subscription API Error: {e}")
        return jsonify(success=False, message="Failed to renew subscription"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@subscription_bp.route('/user/topic-difficulty/<int:user_id>/<int:topic_id>', methods=['GET'])
@require_user_access
def get_topic_difficulty(user_id, topic_id):
    """Get user's difficulty preference for a topic."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT difficulty_level FROM tbl_user_topic_preference 
            WHERE user_id = %s AND topic_id = %s
        """, (user_id, topic_id))
        
        result = cursor.fetchone()
        difficulty = result[0] if result else 'medium'  # Default to medium
        
        return jsonify(success=True, difficulty=difficulty)
        
    except Exception as e:
        print(f"Get Topic Difficulty API Error: {e}")
        return jsonify(success=False, message="Failed to fetch topic difficulty"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@subscription_bp.route('/user/update-topic-difficulty', methods=['POST', 'OPTIONS'])
@require_auth(['student', 'parent'])
def update_topic_difficulty():
    """Update user's difficulty preference for a topic."""
    if request.method == 'OPTIONS':
        return jsonify(success=True)
    
    data = request.get_json()
    user_id = data.get('user_id')
    topic_id = data.get('topic_id')
    difficulty = data.get('difficulty')
    
    if not all([user_id, topic_id, difficulty]):
        return jsonify(success=False, message="Missing required fields"), 400
    
    # Validate difficulty level
    valid_difficulties = ['easy', 'medium', 'hard']
    if difficulty not in valid_difficulties:
        return jsonify(success=False, message="Invalid difficulty level"), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Upsert difficulty preference
        cursor.execute("""
            INSERT INTO tbl_user_topic_preference (user_id, topic_id, difficulty_level, updated_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (user_id, topic_id) 
            DO UPDATE SET difficulty_level = EXCLUDED.difficulty_level, updated_at = NOW()
        """, (user_id, topic_id, difficulty))
        
        conn.commit()
        
        return jsonify(success=True, message="Topic difficulty updated successfully")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Update Topic Difficulty API Error: {e}")
        return jsonify(success=False, message="Failed to update topic difficulty"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)