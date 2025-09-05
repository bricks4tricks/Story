from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import config
from models import db, User, Story, UserProgress, Assignment, Classroom
import json
import os
from datetime import datetime

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app

app = create_app()

# Create database tables
with app.app_context():
    db.create_all()
    
    # Initialize sample data if database is empty
    if Story.query.count() == 0:
        init_sample_data()

# Sample curriculum data based on Florida B.E.S.T. standards
CURRICULUM_DATA = {
    "elementary": {
        "K": {
            "name": "Kindergarten",
            "age_range": "4-5 years",
            "strands": ["Number Sense", "Algebraic Reasoning", "Geometric Reasoning", "Measurement", "Data Analysis"],
            "benchmark_count": 22,
            "sample_stories": [
                {
                    "id": "k_counting_forest",
                    "title": "Counting Creatures in the Enchanted Forest",
                    "strand": "Number Sense and Operations",
                    "benchmark": "MA.K.NSO.1.1",
                    "description": "Help forest animals count objects from 0 to 20",
                    "duration": "5-8 minutes",
                    "difficulty": "Beginner"
                },
                {
                    "id": "k_shape_detective",
                    "title": "Shape Detective Adventures",
                    "strand": "Geometric Reasoning", 
                    "benchmark": "MA.K.GR.1.1",
                    "description": "Identify circles, triangles, rectangles, and squares in a magical kingdom",
                    "duration": "6-10 minutes",
                    "difficulty": "Beginner"
                }
            ]
        },
        "1": {
            "name": "Grade 1",
            "age_range": "5-6 years",
            "strands": ["Number Sense", "Algebraic Reasoning", "Measurement", "Geometric Reasoning", "Data Analysis", "Fractions"],
            "benchmark_count": 26,
            "sample_stories": [
                {
                    "id": "g1_addition_bakery",
                    "title": "The Addition Bakery",
                    "strand": "Algebraic Reasoning",
                    "benchmark": "MA.1.AR.1.1",
                    "description": "Solve addition problems up to 20 while helping a baker",
                    "duration": "8-12 minutes",
                    "difficulty": "Beginner"
                }
            ]
        },
        "2": {
            "name": "Grade 2", 
            "age_range": "6-7 years",
            "strands": ["Number Sense", "Algebraic Reasoning", "Measurement", "Geometric Reasoning", "Data Analysis", "Fractions"],
            "benchmark_count": 27,
            "sample_stories": [
                {
                    "id": "g2_shape_kingdom",
                    "title": "Classifying Shapes in the Kingdom",
                    "strand": "Geometric Reasoning",
                    "benchmark": "MA.2.GR.1.2", 
                    "description": "Compare and sort 2D and 3D shapes in a royal adventure",
                    "duration": "10-15 minutes",
                    "difficulty": "Elementary"
                }
            ]
        }
    },
    "primary": {
        "3": {
            "name": "Grade 3",
            "age_range": "7-8 years", 
            "strands": ["Algebraic Reasoning", "Number Sense", "Geometric Reasoning", "Fractions", "Measurement", "Data Analysis"],
            "benchmark_count": 34,
            "sample_stories": [
                {
                    "id": "g3_multiplication_manor",
                    "title": "The Multiplication Mystery Manor",
                    "strand": "Algebraic Reasoning",
                    "benchmark": "MA.3.AR.1.1",
                    "description": "Apply distributive property to solve multiplication mysteries",
                    "duration": "12-18 minutes", 
                    "difficulty": "Intermediate"
                }
            ]
        },
        "4": {
            "name": "Grade 4",
            "age_range": "8-9 years",
            "strands": ["Number Sense", "Fractions", "Algebraic Reasoning", "Geometric Reasoning", "Measurement", "Data Analysis"],
            "benchmark_count": 39,
            "sample_stories": [
                {
                    "id": "g4_fraction_pirates",
                    "title": "Fraction Pirates",
                    "strand": "Fractions",
                    "benchmark": "MA.4.FR.2.3",
                    "description": "Compare fractions while searching for treasure",
                    "duration": "15-20 minutes",
                    "difficulty": "Intermediate"
                }
            ]
        },
        "5": {
            "name": "Grade 5",
            "age_range": "9-10 years",
            "strands": ["Number Sense", "Algebraic Reasoning", "Geometric Reasoning", "Fractions", "Data Analysis", "Measurement"],
            "benchmark_count": 36,
            "sample_stories": [
                {
                    "id": "g5_coordinate_treasure",
                    "title": "Coordinate Grid Treasure Hunt", 
                    "strand": "Geometric Reasoning",
                    "benchmark": "MA.5.GR.3.1",
                    "description": "Navigate coordinate grids to find hidden treasure",
                    "duration": "18-25 minutes",
                    "difficulty": "Intermediate"
                }
            ]
        }
    },
    "middle_school": {
        "6": {
            "name": "Grade 6",
            "age_range": "10-11 years",
            "strands": ["Number Sense", "Algebraic Reasoning", "Geometric Reasoning", "Data Analysis"],
            "benchmark_count": 40,
            "sample_stories": [
                {
                    "id": "g6_variable_valley",
                    "title": "Algebraic Adventures in Variable Valley",
                    "strand": "Algebraic Reasoning", 
                    "benchmark": "MA.6.AR.1.1",
                    "description": "Translate word problems into algebraic expressions",
                    "duration": "20-25 minutes",
                    "difficulty": "Advanced"
                }
            ]
        },
        "7": {
            "name": "Grade 7",
            "age_range": "11-12 years",
            "strands": ["Algebraic Reasoning", "Data Analysis", "Geometric Reasoning", "Number Sense"],
            "benchmark_count": 34,
            "sample_stories": [
                {
                    "id": "g7_probability_sleuths",
                    "title": "Statistical Sleuths",
                    "strand": "Data Analysis and Probability",
                    "benchmark": "MA.7.DP.1.2", 
                    "description": "Solve crimes using probability and statistics",
                    "duration": "25-30 minutes",
                    "difficulty": "Advanced"
                }
            ]
        },
        "8": {
            "name": "Grade 8",
            "age_range": "12-13 years",
            "strands": ["Algebraic Reasoning", "Geometric Reasoning", "Number Sense", "Data Analysis", "Functions"],
            "benchmark_count": 40,
            "sample_stories": [
                {
                    "id": "g8_function_factory",
                    "title": "Function Machine Factory",
                    "strand": "Functions",
                    "benchmark": "MA.8.F.1.1",
                    "description": "Understand functions through mechanical adventures",
                    "duration": "25-35 minutes",
                    "difficulty": "Advanced"
                }
            ]
        }
    },
    "high_school": {
        "9-12": {
            "name": "High School",
            "age_range": "13-18 years", 
            "strands": ["Algebraic Reasoning", "Data Analysis", "Calculus", "Geometric Reasoning", "Logic", "Financial Literacy", "Functions", "Trigonometry"],
            "benchmark_count": 337,
            "sample_stories": [
                {
                    "id": "hs_calculus_chronicles",
                    "title": "Calculus Chronicles: Rate of Change Adventures",
                    "strand": "Calculus",
                    "benchmark": "MA.912.C.1.2",
                    "description": "Explore limits and continuity through time-travel stories",
                    "duration": "30-45 minutes",
                    "difficulty": "Expert"
                },
                {
                    "id": "hs_financial_freedom", 
                    "title": "Financial Freedom Quest",
                    "strand": "Financial Literacy",
                    "benchmark": "MA.912.FL.3.3",
                    "description": "Learn credit and debt management through real-world scenarios",
                    "duration": "35-50 minutes",
                    "difficulty": "Expert"
                }
            ]
        }
    }
}

@app.route('/')
def home():
    # Get featured stories for homepage
    featured_stories = Story.query.filter_by(featured=True, is_active=True).limit(6).all()
    
    # Get stats for homepage
    stats = {
        'total_stories': Story.query.filter_by(is_active=True).count(),
        'total_users': User.query.filter_by(is_active=True).count(),
        'total_standards': 642  # Static count of FL B.E.S.T. standards
    }
    
    return render_template('index.html', featured_stories=featured_stories, stats=stats)

@app.route('/stories')
def stories():
    # Get filter parameters
    grade_filter = request.args.get('grade', 'all')
    strand_filter = request.args.get('strand', 'all')
    page = request.args.get('page', 1, type=int)
    
    # Build query
    query = Story.query.filter_by(is_active=True)
    
    if grade_filter != 'all':
        if grade_filter == 'elementary':
            query = query.filter(Story.grade_level.in_(['K', '1', '2']))
        elif grade_filter == 'primary':
            query = query.filter(Story.grade_level.in_(['3', '4', '5']))
        elif grade_filter == 'middle_school':
            query = query.filter(Story.grade_level.in_(['6', '7', '8']))
        elif grade_filter == 'high_school':
            query = query.filter(Story.grade_level.in_(['9', '10', '11', '12', '9-12']))
    
    if strand_filter != 'all':
        query = query.filter(Story.math_strand.ilike(f'%{strand_filter.replace("_", " ")}%'))
    
    # Paginate results
    stories_pagination = query.order_by(Story.featured.desc(), Story.created_at.desc())\
                             .paginate(page=page, per_page=12, error_out=False)
    
    # Group stories by category for display
    stories_by_category = {
        'elementary': [],
        'primary': [],
        'middle_school': [],
        'high_school': []
    }
    
    for story in stories_pagination.items:
        stories_by_category[story.grade_category].append(story)
    
    return render_template('stories.html',
                         stories_by_category=stories_by_category,
                         pagination=stories_pagination,
                         current_filters={'grade': grade_filter, 'strand': strand_filter})

@app.route('/story/<story_id>')
def story_detail(story_id):
    story = Story.query.filter_by(story_id=story_id, is_active=True).first_or_404()
    
    # Get user's progress if logged in
    user_progress = None
    if current_user.is_authenticated:
        user_progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            story_id=story.id
        ).first()
        
        # Check if user has access (premium content)
        if story.is_premium and not current_user.is_premium():
            flash('This story requires a premium subscription.', 'warning')
            return redirect(url_for('for_parents'))
    
    # Get related stories
    related_stories = Story.query.filter(
        Story.grade_category == story.grade_category,
        Story.id != story.id,
        Story.is_active == True
    ).limit(3).all()
    
    return render_template('story_detail.html',
                         story=story,
                         user_progress=user_progress,
                         related_stories=related_stories)

@app.route('/for-parents')
def for_parents():
    return render_template('for_parents.html')

@app.route('/for-teachers')
def for_teachers():
    return render_template('for_teachers.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/stories/<grade_level>')
def get_stories_by_grade(grade_level):
    """API endpoint to get stories by grade level"""
    query = Story.query.filter_by(is_active=True)
    
    if grade_level != 'all':
        if grade_level in ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']:
            query = query.filter_by(grade_level=grade_level)
        elif grade_level == 'elementary':
            query = query.filter(Story.grade_level.in_(['K', '1', '2']))
        elif grade_level == 'primary':
            query = query.filter(Story.grade_level.in_(['3', '4', '5']))
        elif grade_level == 'middle_school':
            query = query.filter(Story.grade_level.in_(['6', '7', '8']))
        elif grade_level == 'high_school':
            query = query.filter(Story.grade_level.in_(['9', '10', '11', '12', '9-12']))
    
    stories = query.all()
    
    stories_data = []
    for story in stories:
        stories_data.append({
            'id': story.story_id,
            'title': story.title,
            'description': story.description,
            'strand': story.math_strand,
            'benchmark': story.fl_best_standards[0] if story.fl_best_standards else '',
            'duration': f"{story.estimated_duration} minutes",
            'difficulty': story.difficulty_level,
            'is_premium': story.is_premium
        })
    
    return jsonify({
        'grade': grade_level,
        'stories': stories_data
    })

def init_sample_data():
    """Initialize the database with sample story data"""
    sample_stories = [
        {
            'story_id': 'k_counting_forest',
            'title': 'Counting Creatures in the Enchanted Forest',
            'description': 'Help forest animals count objects from 0 to 20',
            'grade_level': 'K',
            'grade_category': 'elementary',
            'math_strand': 'Number Sense and Operations',
            'fl_best_standards': ['MA.K.NSO.1.1'],
            'difficulty_level': 'Beginner',
            'estimated_duration': 8,
            'is_premium': False,
            'featured': True
        },
        {
            'story_id': 'g1_addition_bakery',
            'title': 'The Addition Bakery',
            'description': 'Solve addition problems up to 20 while helping a baker',
            'grade_level': '1',
            'grade_category': 'elementary',
            'math_strand': 'Algebraic Reasoning',
            'fl_best_standards': ['MA.1.AR.1.1'],
            'difficulty_level': 'Beginner',
            'estimated_duration': 12,
            'is_premium': False,
            'featured': False
        },
        {
            'story_id': 'g3_multiplication_manor',
            'title': 'The Multiplication Mystery Manor',
            'description': 'Apply distributive property to solve multiplication mysteries',
            'grade_level': '3',
            'grade_category': 'primary',
            'math_strand': 'Algebraic Reasoning',
            'fl_best_standards': ['MA.3.AR.1.1'],
            'difficulty_level': 'Intermediate',
            'estimated_duration': 18,
            'is_premium': False,
            'featured': True
        },
        {
            'story_id': 'g5_coordinate_treasure',
            'title': 'Coordinate Grid Treasure Hunt',
            'description': 'Navigate coordinate grids to find hidden treasure',
            'grade_level': '5',
            'grade_category': 'primary',
            'math_strand': 'Geometric Reasoning',
            'fl_best_standards': ['MA.5.GR.3.1'],
            'difficulty_level': 'Intermediate',
            'estimated_duration': 25,
            'is_premium': False,
            'featured': True
        },
        {
            'story_id': 'g6_variable_valley',
            'title': 'Algebraic Adventures in Variable Valley',
            'description': 'Translate word problems into algebraic expressions',
            'grade_level': '6',
            'grade_category': 'middle_school',
            'math_strand': 'Algebraic Reasoning',
            'fl_best_standards': ['MA.6.AR.1.1'],
            'difficulty_level': 'Advanced',
            'estimated_duration': 25,
            'is_premium': False,
            'featured': False
        },
        {
            'story_id': 'hs_financial_freedom',
            'title': 'Financial Freedom Quest',
            'description': 'Learn credit and debt management through real-world scenarios',
            'grade_level': '9-12',
            'grade_category': 'high_school',
            'math_strand': 'Financial Literacy',
            'fl_best_standards': ['MA.912.FL.3.3'],
            'difficulty_level': 'Expert',
            'estimated_duration': 45,
            'is_premium': True,
            'featured': True
        }
    ]
    
    for story_data in sample_stories:
        story = Story(**story_data)
        db.session.add(story)
    
    db.session.commit()
    print(f"Initialized {len(sample_stories)} sample stories")

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() or request.form
        
        # Validate input
        email = data.get('email', '').lower().strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        user_type = data.get('user_type', 'student')
        grade_level = data.get('grade_level', '')
        
        if not all([email, username, password, first_name, last_name]):
            flash('All fields are required.', 'error')
            return redirect(url_for('register'))
        
        # Check if user already exists
        if User.query.filter((User.email == email) | (User.username == username)).first():
            flash('Email or username already exists.', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            grade_level=grade_level if user_type == 'student' else None
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful! Welcome to Logic And Stories.', 'success')
        return redirect(url_for('home'))
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() or request.form
        
        email_or_username = data.get('email_or_username', '').strip()
        password = data.get('password', '')
        remember_me = data.get('remember_me', False)
        
        user = User.query.filter(
            (User.email == email_or_username) | (User.username == email_or_username)
        ).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember_me)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        
        flash('Invalid credentials or account not active.', 'error')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type == 'student':
        return redirect(url_for('student_dashboard'))
    elif current_user.user_type == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    elif current_user.user_type == 'parent':
        return redirect(url_for('parent_dashboard'))
    else:
        return redirect(url_for('home'))

@app.route('/student-dashboard')
@login_required
def student_dashboard():
    if current_user.user_type != 'student':
        return redirect(url_for('dashboard'))
    
    # Get user's progress
    progress_summary = current_user.get_progress_summary()
    
    # Get recent activity
    recent_progress = UserProgress.query.filter_by(user_id=current_user.id)\
                                       .order_by(UserProgress.updated_at.desc())\
                                       .limit(5).all()
    
    # Get recommended stories based on grade level
    recommended_stories = Story.query.filter_by(
        grade_level=current_user.grade_level,
        is_active=True
    ).filter(~Story.id.in_(
        db.session.query(UserProgress.story_id).filter_by(
            user_id=current_user.id,
            is_completed=True
        )
    )).limit(6).all()
    
    return render_template('dashboard/student.html',
                         progress_summary=progress_summary,
                         recent_progress=recent_progress,
                         recommended_stories=recommended_stories)

@app.route('/teacher-dashboard')
@login_required
def teacher_dashboard():
    if current_user.user_type != 'teacher':
        return redirect(url_for('dashboard'))
    
    # Get teacher's classrooms
    classrooms = current_user.classrooms
    
    # Get recent assignments
    recent_assignments = Assignment.query.filter_by(teacher_id=current_user.id)\
                                        .order_by(Assignment.assigned_at.desc())\
                                        .limit(10).all()
    
    # Aggregate statistics
    total_students = sum([len(classroom.students) for classroom in classrooms])
    total_assignments = Assignment.query.filter_by(teacher_id=current_user.id).count()
    
    return render_template('dashboard/teacher.html',
                         classrooms=classrooms,
                         recent_assignments=recent_assignments,
                         total_students=total_students,
                         total_assignments=total_assignments)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)