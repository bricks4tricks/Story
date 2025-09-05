from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # User type: 'student', 'parent', 'teacher', 'admin'
    user_type = db.Column(db.String(20), nullable=False, default='student')
    
    # Profile information
    grade_level = db.Column(db.String(10))  # For students: K, 1, 2, 3, etc.
    school_name = db.Column(db.String(100))
    parent_email = db.Column(db.String(120))  # For student accounts
    
    # Account settings
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    subscription_type = db.Column(db.String(20), default='free')  # free, monthly, annual
    subscription_expires = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    progress_records = db.relationship('UserProgress', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', backref='student', lazy='dynamic', foreign_keys='Assignment.student_id')
    created_assignments = db.relationship('Assignment', backref='teacher', lazy='dynamic', foreign_keys='Assignment.teacher_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_premium(self):
        return self.subscription_type in ['monthly', 'annual'] and \
               (self.subscription_expires is None or self.subscription_expires > datetime.utcnow())
    
    def get_progress_summary(self):
        """Get summary of user's learning progress"""
        progress = db.session.query(UserProgress).filter_by(user_id=self.id).all()
        
        total_stories = len(progress)
        completed_stories = len([p for p in progress if p.completion_percentage >= 100])
        total_time_minutes = sum([p.time_spent_minutes or 0 for p in progress])
        
        # Get standards mastered
        mastered_standards = set()
        for p in progress:
            if p.completion_percentage >= 80:  # Consider 80%+ as mastered
                story = Story.query.get(p.story_id)
                if story and story.fl_best_standards:
                    mastered_standards.update(story.fl_best_standards)
        
        return {
            'total_stories_attempted': total_stories,
            'stories_completed': completed_stories,
            'total_time_minutes': total_time_minutes,
            'standards_mastered': len(mastered_standards),
            'completion_rate': (completed_stories / total_stories * 100) if total_stories > 0 else 0
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class Story(db.Model):
    __tablename__ = 'stories'
    
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.String(50), unique=True, nullable=False, index=True)  # e.g., 'k_counting_forest'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Curriculum alignment
    grade_level = db.Column(db.String(10), nullable=False)  # K, 1, 2, 3, etc.
    grade_category = db.Column(db.String(20), nullable=False)  # elementary, primary, middle_school, high_school
    math_strand = db.Column(db.String(50), nullable=False)  # Number Sense, Algebraic Reasoning, etc.
    fl_best_standards = db.Column(db.JSON)  # List of FL B.E.S.T. benchmarks
    
    # Story metadata
    difficulty_level = db.Column(db.String(20), nullable=False)  # Beginner, Intermediate, Advanced, Expert
    estimated_duration = db.Column(db.Integer)  # Duration in minutes
    story_content = db.Column(db.JSON)  # JSON structure with story steps
    
    # Status and availability
    is_active = db.Column(db.Boolean, default=True)
    is_premium = db.Column(db.Boolean, default=False)
    featured = db.Column(db.Boolean, default=False)
    
    # Analytics
    total_attempts = db.Column(db.Integer, default=0)
    total_completions = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    progress_records = db.relationship('UserProgress', backref='story', lazy='dynamic', cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', backref='story', lazy='dynamic')
    
    @property
    def completion_rate(self):
        return (self.total_completions / self.total_attempts * 100) if self.total_attempts > 0 else 0
    
    def get_average_completion_time(self):
        progress_records = UserProgress.query.filter_by(story_id=self.id, completion_percentage=100).all()
        if progress_records:
            total_time = sum([p.time_spent_minutes or 0 for p in progress_records])
            return total_time / len(progress_records)
        return self.estimated_duration
    
    def __repr__(self):
        return f'<Story {self.story_id}>'

class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    
    # Progress tracking
    completion_percentage = db.Column(db.Integer, default=0)  # 0-100
    current_step = db.Column(db.Integer, default=0)  # Current story step
    total_steps = db.Column(db.Integer)
    
    # Performance metrics
    correct_answers = db.Column(db.Integer, default=0)
    total_attempts = db.Column(db.Integer, default=0)
    hints_used = db.Column(db.Integer, default=0)
    time_spent_minutes = db.Column(db.Integer, default=0)
    
    # Completion data
    is_completed = db.Column(db.Boolean, default=False)
    stars_earned = db.Column(db.Integer, default=0)  # 1-3 stars based on performance
    final_score = db.Column(db.Integer)  # Final score out of 100
    
    # Detailed progress data
    step_data = db.Column(db.JSON)  # JSON with detailed step-by-step progress
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (db.UniqueConstraint('user_id', 'story_id', name='user_story_progress'),)
    
    @property
    def accuracy_rate(self):
        return (self.correct_answers / self.total_attempts * 100) if self.total_attempts > 0 else 0
    
    def calculate_stars(self):
        """Calculate stars earned based on performance"""
        if not self.is_completed:
            return 0
        
        # Base scoring: completion = 1 star
        stars = 1
        
        # Accuracy bonus: >80% accuracy = +1 star
        if self.accuracy_rate >= 80:
            stars += 1
        
        # Efficiency bonus: completed without hints and in good time = +1 star
        if self.hints_used == 0 and self.time_spent_minutes <= (self.story.estimated_duration * 1.2):
            stars += 1
        
        return min(stars, 3)
    
    def __repr__(self):
        return f'<UserProgress {self.user.username} - {self.story.story_id}>'

class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    
    # Assignment details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Due dates and status
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Progress tracking
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    def is_overdue(self):
        return self.due_date and datetime.utcnow() > self.due_date and not self.is_completed
    
    def __repr__(self):
        return f'<Assignment {self.title}>'

class Classroom(db.Model):
    __tablename__ = 'classrooms'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Classroom details
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    grade_level = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(50), default='Mathematics')
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    join_code = db.Column(db.String(10), unique=True)  # For students to join
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('User', backref='classrooms')
    students = db.relationship('User', secondary='classroom_students', backref='enrolled_classrooms')
    
    def generate_join_code(self):
        import random
        import string
        self.join_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return self.join_code
    
    def get_class_progress(self):
        """Get overall class progress statistics"""
        student_ids = [s.id for s in self.students]
        if not student_ids:
            return {'total_students': 0}
        
        progress_records = UserProgress.query.filter(UserProgress.user_id.in_(student_ids)).all()
        
        total_stories = len(set([p.story_id for p in progress_records]))
        completed_stories = len([p for p in progress_records if p.is_completed])
        total_time = sum([p.time_spent_minutes or 0 for p in progress_records])
        
        return {
            'total_students': len(self.students),
            'stories_assigned': total_stories,
            'stories_completed': completed_stories,
            'class_time_minutes': total_time,
            'average_completion_rate': (completed_stories / len(progress_records) * 100) if progress_records else 0
        }
    
    def __repr__(self):
        return f'<Classroom {self.name}>'

# Association table for many-to-many relationship between classrooms and students
classroom_students = db.Table('classroom_students',
    db.Column('classroom_id', db.Integer, db.ForeignKey('classrooms.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)