#!/usr/bin/env python3
"""
Database migration script for Logic And Stories
This script initializes the database and can be run on Render deployment
"""

from app import create_app
from models import db, User, Story, UserProgress, Assignment, Classroom
from config import Config
import os

def init_database():
    """Initialize database with tables and sample data"""
    app = create_app('production')
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully")
        
        # Check if we need to add sample data
        if Story.query.count() == 0:
            print("Initializing sample story data...")
            init_sample_stories()
            print("✓ Sample stories added")
        
        # Create admin user if specified in environment
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        
        if admin_email and admin_password:
            existing_admin = User.query.filter_by(email=admin_email).first()
            if not existing_admin:
                admin_user = User(
                    email=admin_email,
                    username='admin',
                    first_name='Logic And Stories',
                    last_name='Admin',
                    user_type='admin',
                    is_verified=True,
                    subscription_type='annual'
                )
                admin_user.set_password(admin_password)
                db.session.add(admin_user)
                db.session.commit()
                print("✓ Admin user created")
            else:
                print("✓ Admin user already exists")
        
        print("Database initialization complete!")

def init_sample_stories():
    """Initialize the database with comprehensive sample story data"""
    
    sample_stories = [
        # Elementary (K-2) Stories
        {
            'story_id': 'k_counting_forest',
            'title': 'Counting Creatures in the Enchanted Forest',
            'description': 'Help magical forest animals count objects from 0 to 20 in this delightful adventure.',
            'grade_level': 'K',
            'grade_category': 'elementary',
            'math_strand': 'Number Sense and Operations',
            'fl_best_standards': ['MA.K.NSO.1.1', 'MA.K.NSO.1.2'],
            'difficulty_level': 'Beginner',
            'estimated_duration': 8,
            'is_premium': False,
            'featured': True,
            'story_content': {
                'steps': 4,
                'interactive_elements': ['counting', 'number_recognition'],
                'assessment_points': 3
            }
        },
        {
            'story_id': 'k_shape_detective',
            'title': 'Shape Detective Adventures',
            'description': 'Identify circles, triangles, rectangles, and squares in a magical kingdom.',
            'grade_level': 'K',
            'grade_category': 'elementary',
            'math_strand': 'Geometric Reasoning',
            'fl_best_standards': ['MA.K.GR.1.1', 'MA.K.GR.1.2'],
            'difficulty_level': 'Beginner',
            'estimated_duration': 10,
            'is_premium': False,
            'featured': False
        },
        {
            'story_id': 'g1_addition_bakery',
            'title': 'The Addition Bakery',
            'description': 'Solve addition problems up to 20 while helping a friendly baker create delicious treats.',
            'grade_level': '1',
            'grade_category': 'elementary',
            'math_strand': 'Algebraic Reasoning',
            'fl_best_standards': ['MA.1.AR.1.1', 'MA.1.AR.1.2'],
            'difficulty_level': 'Beginner',
            'estimated_duration': 12,
            'is_premium': False,
            'featured': True
        },
        {
            'story_id': 'g2_shape_kingdom',
            'title': 'Classifying Shapes in the Kingdom',
            'description': 'Compare and sort 2D and 3D shapes in a royal adventure through the Shape Kingdom.',
            'grade_level': '2',
            'grade_category': 'elementary',
            'math_strand': 'Geometric Reasoning',
            'fl_best_standards': ['MA.2.GR.1.2', 'MA.2.GR.1.3'],
            'difficulty_level': 'Elementary',
            'estimated_duration': 15,
            'is_premium': False,
            'featured': False
        },
        
        # Primary (3-5) Stories
        {
            'story_id': 'g3_multiplication_manor',
            'title': 'The Multiplication Mystery Manor',
            'description': 'Apply the distributive property to solve multiplication mysteries in this spooky manor.',
            'grade_level': '3',
            'grade_category': 'primary',\n            'math_strand': 'Algebraic Reasoning',\n            'fl_best_standards': ['MA.3.AR.1.1', 'MA.3.AR.1.2'],\n            'difficulty_level': 'Intermediate',\n            'estimated_duration': 18,\n            'is_premium': False,\n            'featured': True\n        },\n        {\n            'story_id': 'g4_fraction_pirates',\n            'title': 'Fraction Pirates',\n            'description': 'Compare fractions while searching for treasure with Captain Fraction and his crew.',\n            'grade_level': '4',\n            'grade_category': 'primary',\n            'math_strand': 'Fractions',\n            'fl_best_standards': ['MA.4.FR.2.3', 'MA.4.FR.2.4'],\n            'difficulty_level': 'Intermediate',\n            'estimated_duration': 20,\n            'is_premium': False,\n            'featured': True\n        },\n        {\n            'story_id': 'g5_coordinate_treasure',\n            'title': 'Coordinate Grid Treasure Hunt',\n            'description': 'Navigate coordinate grids and plot points to discover hidden pirate treasure.',\n            'grade_level': '5',\n            'grade_category': 'primary',\n            'math_strand': 'Geometric Reasoning',\n            'fl_best_standards': ['MA.5.GR.3.1', 'MA.5.GR.3.2'],\n            'difficulty_level': 'Intermediate',\n            'estimated_duration': 25,\n            'is_premium': False,\n            'featured': True\n        },\n        \n        # Middle School (6-8) Stories\n        {\n            'story_id': 'g6_variable_valley',\n            'title': 'Algebraic Adventures in Variable Valley',\n            'description': 'Translate word problems into algebraic expressions in this mathematical adventure.',\n            'grade_level': '6',\n            'grade_category': 'middle_school',\n            'math_strand': 'Algebraic Reasoning',\n            'fl_best_standards': ['MA.6.AR.1.1', 'MA.6.AR.1.2'],\n            'difficulty_level': 'Advanced',\n            'estimated_duration': 25,\n            'is_premium': False,\n            'featured': False\n        },\n        {\n            'story_id': 'g7_probability_sleuths',\n            'title': 'Statistical Sleuths',\n            'description': 'Solve crimes using probability and statistics in this detective mystery.',\n            'grade_level': '7',\n            'grade_category': 'middle_school',\n            'math_strand': 'Data Analysis and Probability',\n            'fl_best_standards': ['MA.7.DP.1.2', 'MA.7.DP.2.1'],\n            'difficulty_level': 'Advanced',\n            'estimated_duration': 30,\n            'is_premium': False,\n            'featured': True\n        },\n        {\n            'story_id': 'g8_function_factory',\n            'title': 'Function Machine Factory',\n            'description': 'Understand functions through mechanical adventures in the Function Factory.',\n            'grade_level': '8',\n            'grade_category': 'middle_school',\n            'math_strand': 'Functions',\n            'fl_best_standards': ['MA.8.F.1.1', 'MA.8.F.1.2'],\n            'difficulty_level': 'Advanced',\n            'estimated_duration': 35,\n            'is_premium': False,\n            'featured': False\n        },\n        \n        # High School (9-12) Stories\n        {\n            'story_id': 'hs_calculus_chronicles',\n            'title': 'Calculus Chronicles: Rate of Change Adventures',\n            'description': 'Explore limits and continuity through time-travel stories and mathematical discoveries.',\n            'grade_level': '9-12',\n            'grade_category': 'high_school',\n            'math_strand': 'Calculus',\n            'fl_best_standards': ['MA.912.C.1.2', 'MA.912.C.2.1'],\n            'difficulty_level': 'Expert',\n            'estimated_duration': 45,\n            'is_premium': True,\n            'featured': True\n        },\n        {\n            'story_id': 'hs_financial_freedom',\n            'title': 'Financial Freedom Quest',\n            'description': 'Learn credit and debt management through real-world scenarios and financial planning.',\n            'grade_level': '9-12',\n            'grade_category': 'high_school',\n            'math_strand': 'Financial Literacy',\n            'fl_best_standards': ['MA.912.FL.3.3', 'MA.912.FL.3.4'],\n            'difficulty_level': 'Expert',\n            'estimated_duration': 50,\n            'is_premium': True,\n            'featured': True\n        },\n        {\n            'story_id': 'hs_trigonometry_travels',\n            'title': 'Trigonometry Travels',\n            'description': 'Journey through ancient civilizations while mastering trigonometric concepts.',\n            'grade_level': '9-12',\n            'grade_category': 'high_school',\n            'math_strand': 'Trigonometry',\n            'fl_best_standards': ['MA.912.T.1.1', 'MA.912.T.1.2'],\n            'difficulty_level': 'Expert',\n            'estimated_duration': 40,\n            'is_premium': True,\n            'featured': False\n        }\n    ]\n    \n    for story_data in sample_stories:\n        story = Story(**story_data)\n        db.session.add(story)\n    \n    db.session.commit()\n    print(f\"✓ Added {len(sample_stories)} sample stories to database\")\n\nif __name__ == '__main__':\n    init_database()