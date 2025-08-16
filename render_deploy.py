"""
Deployment utilities for Render platform.

This module provides utilities to help with Render deployment,
including startup scripts and health checks.
"""

import os
import sys
import subprocess
from migration_manager import MigrationManager


def run_migrations():
    """Run database migrations on startup."""
    try:
        print("🔄 Running database migrations...")
        manager = MigrationManager()
        success = manager.migrate()
        
        if success:
            print("✅ Database migrations completed successfully")
            return True
        else:
            print("❌ Database migrations failed")
            return False
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False


def check_environment():
    """Check that required environment variables are set."""
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'FLASK_ENV'
    ]
    
    missing = []
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        return False
    
    print("✅ Environment variables check passed")
    return True


def install_dependencies():
    """Install Python dependencies."""
    try:
        print("📦 Installing Python dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def build_css():
    """Build CSS assets using Tailwind."""
    try:
        print("🎨 Building CSS assets...")
        
        # Check if npm is available and package.json exists
        if os.path.exists('package.json'):
            subprocess.run(['npm', 'ci'], check=True, capture_output=True, text=True)
            subprocess.run(['npm', 'run', 'build:css'], check=True, capture_output=True, text=True)
            print("✅ CSS assets built successfully")
        else:
            print("⚠️  No package.json found, skipping CSS build")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build CSS: {e}")
        return False
    except FileNotFoundError:
        print("⚠️  npm not found, skipping CSS build")
        return True


def startup_checks():
    """Run all startup checks and preparations."""
    print("🚀 Starting LogicAndStories deployment on Render...")
    
    checks = [
        ("Environment Check", check_environment),
        ("Install Dependencies", install_dependencies),
        ("Build CSS Assets", build_css),
        ("Run Migrations", run_migrations),
    ]
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}...")
        if not check_func():
            print(f"💥 Deployment failed at: {check_name}")
            sys.exit(1)
    
    print("\n🎉 Deployment preparation completed successfully!")
    print("🌐 Starting Flask application...")


if __name__ == "__main__":
    startup_checks()