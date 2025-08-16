"""
Database migration management system for LogicAndStories.

This module provides a simple migration system to manage database schema changes
in a version-controlled manner.
"""

import os
import re
import traceback
from datetime import datetime
from typing import List, Dict, Optional
from db_utils import get_db_connection, release_db_connection


class MigrationManager:
    """Manages database migrations."""
    
    def __init__(self, migrations_dir: str = "migrations"):
        self.migrations_dir = migrations_dir
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Create migrations tracking table if it doesn't exist."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(255) UNIQUE NOT NULL,
                    description TEXT,
                    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    checksum VARCHAR(64)
                )
            """)
            conn.commit()
        except Exception as e:
            print(f"Error creating migrations table: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM migrations ORDER BY applied_at")
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting applied migrations: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)
    
    def get_pending_migrations(self) -> List[Dict[str, str]]:
        """Get list of pending migrations."""
        applied = set(self.get_applied_migrations())
        available = self._get_available_migrations()
        
        pending = []
        for migration in available:
            if migration['version'] not in applied:
                pending.append(migration)
        
        return sorted(pending, key=lambda x: x['version'])
    
    def _get_available_migrations(self) -> List[Dict[str, str]]:
        """Get list of all available migration files."""
        migrations = []
        
        if not os.path.exists(self.migrations_dir):
            return migrations
        
        for filename in os.listdir(self.migrations_dir):
            if filename.endswith('.sql'):
                # Extract version from filename (e.g., 001_initial_schema.sql)
                match = re.match(r'^(\d+)_(.+)\.sql$', filename)
                if match:
                    version = match.group(1)
                    description = match.group(2).replace('_', ' ').title()
                    migrations.append({
                        'version': version,
                        'description': description,
                        'filename': filename,
                        'filepath': os.path.join(self.migrations_dir, filename)
                    })
        
        return sorted(migrations, key=lambda x: x['version'])
    
    def apply_migration(self, migration: Dict[str, str]) -> bool:
        """Apply a single migration."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Read migration file
            with open(migration['filepath'], 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Execute migration
            cursor.execute(sql_content)
            
            # Record migration as applied
            cursor.execute("""
                INSERT INTO migrations (version, description)
                VALUES (%s, %s)
            """, (migration['version'], migration['description']))
            
            conn.commit()
            print(f"✓ Applied migration {migration['version']}: {migration['description']}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to apply migration {migration['version']}: {e}")
            traceback.print_exc()
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)
    
    def migrate(self) -> bool:
        """Apply all pending migrations."""
        pending = self.get_pending_migrations()
        
        if not pending:
            print("No pending migrations.")
            return True
        
        print(f"Found {len(pending)} pending migrations:")
        for migration in pending:
            print(f"  - {migration['version']}: {migration['description']}")
        
        success = True
        for migration in pending:
            if not self.apply_migration(migration):
                success = False
                break
        
        if success:
            print("All migrations applied successfully!")
        else:
            print("Migration failed. Please check the errors above.")
        
        return success
    
    def create_migration(self, description: str) -> str:
        """Create a new migration file."""
        # Generate version number
        existing = self._get_available_migrations()
        if existing:
            last_version = int(max(existing, key=lambda x: x['version'])['version'])
            version = f"{last_version + 1:03d}"
        else:
            version = "001"
        
        # Create filename
        safe_description = re.sub(r'[^\w\s-]', '', description)
        safe_description = re.sub(r'[-\s]+', '_', safe_description).lower()
        filename = f"{version}_{safe_description}.sql"
        filepath = os.path.join(self.migrations_dir, filename)
        
        # Create migrations directory if it doesn't exist
        os.makedirs(self.migrations_dir, exist_ok=True)
        
        # Create migration file with template
        template = f"""-- Migration {version}: {description}
-- Created: {datetime.now().isoformat()}

-- Add your SQL statements here
-- Example:
-- CREATE TABLE example (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(255) NOT NULL
-- );
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"Created migration: {filepath}")
        return filepath


def main():
    """CLI interface for migration management."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migration_manager.py <command> [args]")
        print("Commands:")
        print("  migrate              - Apply all pending migrations")
        print("  status               - Show migration status")
        print("  create <description> - Create a new migration")
        return
    
    manager = MigrationManager()
    command = sys.argv[1]
    
    if command == "migrate":
        manager.migrate()
    elif command == "status":
        applied = manager.get_applied_migrations()
        pending = manager.get_pending_migrations()
        
        print(f"Applied migrations ({len(applied)}):")
        for version in applied:
            print(f"  ✓ {version}")
        
        print(f"\nPending migrations ({len(pending)}):")
        for migration in pending:
            print(f"  - {migration['version']}: {migration['description']}")
    
    elif command == "create":
        if len(sys.argv) < 3:
            print("Usage: python migration_manager.py create <description>")
            return
        description = " ".join(sys.argv[2:])
        manager.create_migration(description)
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()