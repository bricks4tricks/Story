"""
Analytics and Progress Tracking Routes
Provides endpoints for gamification and progress visualization
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime, timedelta, timezone
from auth_utils import require_auth, require_user_access
from db_utils import get_db_connection, release_db_connection
import traceback

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api')


@analytics_bp.route('/progress/analytics', methods=['GET'])
@require_auth(['student', 'parent', 'admin'])
def get_progress_analytics():
    """Get comprehensive progress analytics for charts."""
    user_id = g.current_user['user_id']
    
    # For parents, get aggregated data from their children
    if g.current_user['user_type'] == 'parent':
        user_id = request.args.get('child_id', user_id)
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        analytics_data = {
            'weeklyProgress': get_weekly_progress(cursor, user_id),
            'subjectPerformance': get_subject_performance(cursor, user_id),
            'streakData': get_streak_data(cursor, user_id),
            'accuracyTrend': get_accuracy_trend(cursor, user_id)
        }
        
        return jsonify(analytics_data), 200
        
    except Exception as e:
        print(f"Get Progress Analytics Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Failed to fetch analytics"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@analytics_bp.route('/gamification/progress', methods=['GET'])
@require_auth(['student', 'parent', 'admin'])
def get_gamification_progress():
    """Get user's gamification progress."""
    user_id = g.current_user['user_id']
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user gamification data
        cursor.execute("""
            SELECT total_points, current_level, badges_earned, 
                   reading_streak_current, reading_streak_longest
            FROM tbl_user_gamification 
            WHERE user_id = %s
        """, (user_id,))
        
        gamification_data = cursor.fetchone()
        
        if not gamification_data:
            # Initialize if doesn't exist
            cursor.execute("""
                INSERT INTO tbl_user_gamification (user_id) 
                VALUES (%s) RETURNING total_points, current_level, badges_earned, 
                       reading_streak_current, reading_streak_longest
            """, (user_id,))
            gamification_data = cursor.fetchone()
            conn.commit()
        
        return jsonify({
            "points": gamification_data[0],
            "level": gamification_data[1],
            "badges": gamification_data[2] or [],
            "currentStreak": gamification_data[3],
            "longestStreak": gamification_data[4]
        }), 200
        
    except Exception as e:
        print(f"Get Gamification Progress Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Failed to fetch gamification data"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@analytics_bp.route('/gamification/progress', methods=['POST'])
@require_auth(['student', 'parent', 'admin'])
def update_gamification_progress():
    """Update user's gamification progress."""
    user_id = g.current_user['user_id']
    data = request.get_json(silent=True) or {}
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update gamification data
        cursor.execute("""
            UPDATE tbl_user_gamification 
            SET total_points = %s, current_level = %s, badges_earned = %s,
                last_activity_date = CURRENT_DATE
            WHERE user_id = %s
        """, (
            data.get('points', 0),
            data.get('level', 1),
            data.get('badges', []),
            user_id
        ))
        
        if cursor.rowcount == 0:
            # Insert if doesn't exist
            cursor.execute("""
                INSERT INTO tbl_user_gamification 
                (user_id, total_points, current_level, badges_earned, last_activity_date)
                VALUES (%s, %s, %s, %s, CURRENT_DATE)
            """, (
                user_id,
                data.get('points', 0),
                data.get('level', 1),
                data.get('badges', [])
            ))
        
        conn.commit()
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        print(f"Update Gamification Progress Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Failed to update progress"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@analytics_bp.route('/activity/record', methods=['POST'])
@require_auth(['student', 'parent', 'admin'])
def record_activity():
    """Record user activity for analytics."""
    user_id = g.current_user['user_id']
    data = request.get_json(silent=True) or {}
    
    activity_type = data.get('type')  # 'story_read', 'quiz_completed', etc.
    activity_data = data.get('data', {})
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        current_date = datetime.now(timezone.utc).date()
        current_time = datetime.now(timezone.utc).time()
        
        # Update daily activity
        if activity_type == 'story_read':
            update_daily_activity_story(cursor, user_id, current_date, current_time, activity_data)
        elif activity_type == 'quiz_completed':
            update_daily_activity_quiz(cursor, user_id, current_date, current_time, activity_data)
        
        # Update subject performance
        subject = activity_data.get('subject')
        if subject:
            update_subject_performance(cursor, user_id, subject, activity_type, activity_data)
        
        # Update reading streak
        update_reading_streak(cursor, user_id, current_date)
        
        conn.commit()
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        print(f"Record Activity Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Failed to record activity"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


@analytics_bp.route('/leaderboard', methods=['GET'])
@require_auth(['student', 'parent', 'admin'])
def get_leaderboard():
    """Get leaderboard data."""
    leaderboard_type = request.args.get('type', 'points')  # points, streak, stories
    limit = min(int(request.args.get('limit', 10)), 50)
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if leaderboard_type == 'points':
            cursor.execute("""
                SELECT u.username, g.total_points, g.current_level
                FROM tbl_user_gamification g
                JOIN tbl_user u ON g.user_id = u.id
                WHERE u.usertype != 'Admin'
                ORDER BY g.total_points DESC
                LIMIT %s
            """, (limit,))
        elif leaderboard_type == 'streak':
            cursor.execute("""
                SELECT u.username, g.reading_streak_current, g.reading_streak_longest
                FROM tbl_user_gamification g
                JOIN tbl_user u ON g.user_id = u.id
                WHERE u.usertype != 'Admin'
                ORDER BY g.reading_streak_current DESC, g.reading_streak_longest DESC
                LIMIT %s
            """, (limit,))
        elif leaderboard_type == 'stories':
            cursor.execute("""
                SELECT u.username, COALESCE(SUM(da.stories_read), 0) as total_stories
                FROM tbl_user u
                LEFT JOIN tbl_daily_activity da ON u.id = da.user_id
                WHERE u.usertype != 'Admin'
                GROUP BY u.id, u.username
                ORDER BY total_stories DESC
                LIMIT %s
            """, (limit,))
        
        results = cursor.fetchall()
        leaderboard = []
        
        for i, result in enumerate(results):
            if leaderboard_type == 'points':
                leaderboard.append({
                    'rank': i + 1,
                    'username': result[0],
                    'points': result[1],
                    'level': result[2]
                })
            elif leaderboard_type == 'streak':
                leaderboard.append({
                    'rank': i + 1,
                    'username': result[0],
                    'currentStreak': result[1],
                    'longestStreak': result[2]
                })
            elif leaderboard_type == 'stories':
                leaderboard.append({
                    'rank': i + 1,
                    'username': result[0],
                    'totalStories': result[1]
                })
        
        return jsonify(leaderboard), 200
        
    except Exception as e:
        print(f"Get Leaderboard Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Failed to fetch leaderboard"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)


def get_weekly_progress(cursor, user_id):
    """Get weekly progress data for charts."""
    # Get last 7 days of activity
    cursor.execute("""
        SELECT activity_date, stories_read, quizzes_completed
        FROM tbl_daily_activity
        WHERE user_id = %s 
        AND activity_date >= CURRENT_DATE - INTERVAL '7 days'
        ORDER BY activity_date
    """, (user_id,))
    
    results = cursor.fetchall()
    
    # Create labels for last 7 days
    labels = []
    stories_completed = []
    
    for i in range(7):
        date = datetime.now().date() - timedelta(days=6-i)
        labels.append(date.strftime('%a'))
        
        # Find data for this date
        stories_count = 0
        for result in results:
            if result[0] == date:
                stories_count = result[1]
                break
        
        stories_completed.append(stories_count)
    
    return {
        'labels': labels,
        'storiesCompleted': stories_completed
    }


def get_subject_performance(cursor, user_id):
    """Get subject performance data for doughnut chart."""
    cursor.execute("""
        SELECT subject_name, stories_completed, average_accuracy
        FROM tbl_subject_performance
        WHERE user_id = %s
        ORDER BY stories_completed DESC
        LIMIT 5
    """, (user_id,))
    
    results = cursor.fetchall()
    
    if not results:
        return {
            'subjects': ['Reading', 'Math', 'Science'],
            'scores': [45, 30, 25]
        }
    
    subjects = [result[0] for result in results]
    scores = [result[1] for result in results]
    
    return {
        'subjects': subjects,
        'scores': scores
    }


def get_streak_data(cursor, user_id):
    """Get reading streak data for bar chart."""
    cursor.execute("""
        SELECT activity_date, stories_read
        FROM tbl_daily_activity
        WHERE user_id = %s 
        AND activity_date >= CURRENT_DATE - INTERVAL '7 days'
        ORDER BY activity_date
    """, (user_id,))
    
    results = cursor.fetchall()
    
    days = []
    streak_counts = []
    
    for i in range(7):
        date = datetime.now().date() - timedelta(days=6-i)
        days.append(date.strftime('%a'))
        
        # Find stories read for this date
        stories_count = 0
        for result in results:
            if result[0] == date:
                stories_count = result[1]
                break
        
        streak_counts.append(1 if stories_count > 0 else 0)
    
    return {
        'days': days,
        'streakCounts': streak_counts
    }


def get_accuracy_trend(cursor, user_id):
    """Get quiz accuracy trend for area chart."""
    cursor.execute("""
        SELECT activity_date, 
               CASE 
                   WHEN quiz_questions_answered > 0 
                   THEN ROUND((quiz_accuracy_total::DECIMAL / quiz_questions_answered) * 100, 1)
                   ELSE 0 
               END as accuracy_percentage
        FROM tbl_daily_activity
        WHERE user_id = %s 
        AND activity_date >= CURRENT_DATE - INTERVAL '7 days'
        AND quiz_questions_answered > 0
        ORDER BY activity_date
    """, (user_id,))
    
    results = cursor.fetchall()
    
    dates = [result[0].strftime('%m/%d') for result in results]
    accuracy_percentages = [float(result[1]) for result in results]
    
    # Fill in missing days with previous value or 0
    if len(dates) < 7:
        all_dates = []
        all_accuracies = []
        
        for i in range(7):
            date = datetime.now().date() - timedelta(days=6-i)
            all_dates.append(date.strftime('%m/%d'))
            
            # Find accuracy for this date
            accuracy = 0
            for j, result_date in enumerate([r[0] for r in results]):
                if result_date == date:
                    accuracy = float(results[j][1])
                    break
            
            all_accuracies.append(accuracy)
        
        dates = all_dates
        accuracy_percentages = all_accuracies
    
    return {
        'dates': dates,
        'accuracyPercentages': accuracy_percentages
    }


def update_daily_activity_story(cursor, user_id, date, time, data):
    """Update daily activity for story reading."""
    cursor.execute("""
        INSERT INTO tbl_daily_activity 
        (user_id, activity_date, stories_read, first_activity_time, last_activity_time)
        VALUES (%s, %s, 1, %s, %s)
        ON CONFLICT (user_id, activity_date) 
        DO UPDATE SET 
            stories_read = tbl_daily_activity.stories_read + 1,
            last_activity_time = %s,
            first_activity_time = LEAST(tbl_daily_activity.first_activity_time, %s)
    """, (user_id, date, time, time, time, time))


def update_daily_activity_quiz(cursor, user_id, date, time, data):
    """Update daily activity for quiz completion."""
    correct_answers = data.get('correctAnswers', 0)
    total_questions = data.get('totalQuestions', 0)
    is_perfect = correct_answers == total_questions and total_questions > 0
    
    cursor.execute("""
        INSERT INTO tbl_daily_activity 
        (user_id, activity_date, quizzes_completed, quiz_accuracy_total, 
         quiz_questions_answered, perfect_quizzes, first_activity_time, last_activity_time)
        VALUES (%s, %s, 1, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id, activity_date) 
        DO UPDATE SET 
            quizzes_completed = tbl_daily_activity.quizzes_completed + 1,
            quiz_accuracy_total = tbl_daily_activity.quiz_accuracy_total + %s,
            quiz_questions_answered = tbl_daily_activity.quiz_questions_answered + %s,
            perfect_quizzes = tbl_daily_activity.perfect_quizzes + %s,
            last_activity_time = %s,
            first_activity_time = LEAST(tbl_daily_activity.first_activity_time, %s)
    """, (
        user_id, date, correct_answers, total_questions, 1 if is_perfect else 0, time, time,
        correct_answers, total_questions, 1 if is_perfect else 0, time, time
    ))


def update_subject_performance(cursor, user_id, subject, activity_type, data):
    """Update subject performance tracking."""
    if activity_type == 'story_read':
        cursor.execute("""
            INSERT INTO tbl_subject_performance 
            (user_id, subject_name, stories_completed, last_accessed)
            VALUES (%s, %s, 1, NOW())
            ON CONFLICT (user_id, subject_name) 
            DO UPDATE SET 
                stories_completed = tbl_subject_performance.stories_completed + 1,
                last_accessed = NOW()
        """, (user_id, subject))
    elif activity_type == 'quiz_completed':
        correct_answers = data.get('correctAnswers', 0)
        total_questions = data.get('totalQuestions', 0)
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        cursor.execute("""
            INSERT INTO tbl_subject_performance 
            (user_id, subject_name, quizzes_completed, average_accuracy, last_accessed)
            VALUES (%s, %s, 1, %s, NOW())
            ON CONFLICT (user_id, subject_name) 
            DO UPDATE SET 
                quizzes_completed = tbl_subject_performance.quizzes_completed + 1,
                average_accuracy = (tbl_subject_performance.average_accuracy * tbl_subject_performance.quizzes_completed + %s) / (tbl_subject_performance.quizzes_completed + 1),
                last_accessed = NOW()
        """, (user_id, subject, accuracy, accuracy))


def update_reading_streak(cursor, user_id, date):
    """Update user's reading streak."""
    # Check if user read yesterday
    yesterday = date - timedelta(days=1)
    
    cursor.execute("""
        SELECT stories_read FROM tbl_daily_activity 
        WHERE user_id = %s AND activity_date = %s
    """, (user_id, yesterday))
    
    yesterday_activity = cursor.fetchone()
    
    # Get current gamification data
    cursor.execute("""
        SELECT reading_streak_current, reading_streak_longest, last_activity_date
        FROM tbl_user_gamification 
        WHERE user_id = %s
    """, (user_id,))
    
    gamification_data = cursor.fetchone()
    
    if gamification_data:
        current_streak, longest_streak, last_activity = gamification_data
        
        # Determine new streak
        if last_activity == yesterday and yesterday_activity and yesterday_activity[0] > 0:
            # Continue streak
            new_streak = current_streak + 1
        elif last_activity == date:
            # Same day activity
            new_streak = current_streak
        else:
            # Start new streak
            new_streak = 1
        
        new_longest = max(longest_streak, new_streak)
        
        cursor.execute("""
            UPDATE tbl_user_gamification 
            SET reading_streak_current = %s, 
                reading_streak_longest = %s, 
                last_activity_date = %s
            WHERE user_id = %s
        """, (new_streak, new_longest, date, user_id))
    else:
        # Initialize gamification data
        cursor.execute("""
            INSERT INTO tbl_user_gamification 
            (user_id, reading_streak_current, reading_streak_longest, last_activity_date)
            VALUES (%s, 1, 1, %s)
        """, (user_id, date))