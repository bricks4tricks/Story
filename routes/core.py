"""
Core application routes.

Contains basic routes like health checks, CSRF tokens, and static content.
"""

from flask import Blueprint, jsonify, render_template, send_from_directory
from security_utils import get_csrf_token

core_bp = Blueprint('core', __name__)


@core_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({"status": "ok", "service": "LogicAndStories"}), 200


@core_bp.route("/api/csrf-token", methods=["GET"])
def get_csrf_token_endpoint():
    """Endpoint to get CSRF token for API requests."""
    return jsonify({"csrf_token": get_csrf_token()}), 200


@core_bp.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@core_bp.route('/dashboard')
def dashboard():
    """Serve the dashboard page."""
    return render_template('dashboard.html')


@core_bp.route('/signin')
def signin():
    """Serve the signin page."""
    return render_template('signin.html')


@core_bp.route('/signup')
def signup():
    """Serve the signup page."""
    return render_template('signup.html')


@core_bp.route('/choose-plan')
def choose_plan():
    """Serve the plan selection page."""
    return render_template('choose-plan.html')


@core_bp.route('/settings')
def settings():
    """Serve the settings page."""
    return render_template('settings.html')


@core_bp.route('/forgot-password')
def forgot_password():
    """Serve the forgot password page."""
    return render_template('forgot-password.html')


@core_bp.route('/reset-password')
def reset_password():
    """Serve the reset password page."""
    return render_template('reset-password.html')


@core_bp.route('/story-player')
def story_player():
    """Serve the story player page."""
    return render_template('story-player.html')


@core_bp.route('/quiz-player')
def quiz_player():
    """Serve the quiz player page."""
    return render_template('quiz-player.html')


@core_bp.route('/video-player')
def video_player():
    """Serve the video player page."""
    return render_template('video-player.html')


@core_bp.route('/leaderboard')
def leaderboard():
    """Serve the leaderboard page."""
    return render_template('leaderboard.html')


@core_bp.route('/parent-portal')
def parent_portal():
    """Serve the parent portal page."""
    return render_template('parent-portal.html')


@core_bp.route('/progress-dashboard')
def progress_dashboard():
    """Serve the progress dashboard page."""
    return render_template('progress-dashboard.html')


@core_bp.route('/blog')
def blog():
    """Serve the blog page."""
    return render_template('blog.html')


@core_bp.route('/privacy-policy')
def privacy_policy():
    """Serve the privacy policy page."""
    return render_template('privacy-policy.html')


@core_bp.route('/terms-of-service')
def terms_of_service():
    """Serve the terms of service page."""
    return render_template('terms-of-service.html')


@core_bp.route('/favicon.ico')
def favicon():
    """Serve the favicon."""
    return send_from_directory('static', 'favicon.ico')