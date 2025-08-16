# Database Schema Documentation

This document describes the database schema for the LogicAndStories educational platform.

## Overview

The LogicAndStories platform uses PostgreSQL as its primary database. The schema is designed to support:
- User management (parents, students, admins)
- Educational content organization (subjects, topics, questions)
- Session management and authentication
- Subscription management
- User preferences and progress tracking

## Database Tables

### User Management

#### `tbl_user`
Main user table storing all user types (Admin, Parent, Student).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Unique user identifier |
| `username` | VARCHAR(255) | UNIQUE, NOT NULL | User's login name |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User's email address |
| `passwordhash` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `usertype` | VARCHAR(50) | NOT NULL, DEFAULT 'Parent' | User role: Admin, Parent, Student |
| `parentuserid` | INTEGER | FK to tbl_user(id) | Parent ID for student accounts |
| `createdon` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Account creation timestamp |
| `plan` | VARCHAR(20) | DEFAULT 'Monthly' | Subscription plan type |
| `resettoken` | VARCHAR(255) | NULL | Password reset token |
| `resettokenexpiry` | TIMESTAMP WITH TIME ZONE | NULL | Reset token expiration |

**Indexes:**
- `idx_user_username` on `username`
- `idx_user_email` on `email`

**Relationships:**
- Self-referential FK: `parentuserid` → `tbl_user(id)`

---

#### `tbl_subscription`
Subscription status and expiration tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Subscription record ID |
| `user_id` | INTEGER | UNIQUE, FK to tbl_user(id) | User associated with subscription |
| `active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Subscription status |
| `expires_on` | TIMESTAMP WITH TIME ZONE | NULL | Subscription expiration date |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Subscription creation date |

**Indexes:**
- `idx_subscription_user_id` on `user_id`

**Relationships:**
- FK: `user_id` → `tbl_user(id)` ON DELETE CASCADE

---

#### `tbl_userpreferences`
User-specific application preferences.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | INTEGER | PRIMARY KEY, FK to tbl_user(id) | User ID |
| `darkmode` | BOOLEAN | NOT NULL, DEFAULT FALSE | Dark mode preference |
| `fontsize` | VARCHAR(10) | NOT NULL, DEFAULT 'medium' | Font size preference |

**Relationships:**
- FK: `user_id` → `tbl_user(id)` ON DELETE CASCADE

---

### Session Management

#### `tbl_user_session`
Session tokens for regular user authentication.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Session record ID |
| `user_id` | INTEGER | NOT NULL, FK to tbl_user(id) | User ID |
| `session_token` | VARCHAR(255) | UNIQUE, NOT NULL | Session token |
| `user_type` | VARCHAR(20) | NOT NULL, DEFAULT 'student' | User type for quick access |
| `expires_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | Session expiration |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Session creation time |

**Constraints:**
- UNIQUE constraint on `user_id` (one session per user)

**Indexes:**
- `idx_user_session_token` on `session_token`
- `idx_user_session_expires` on `expires_at`
- `idx_user_session_user_id` on `user_id`

**Relationships:**
- FK: `user_id` → `tbl_user(id)` ON DELETE CASCADE

---

#### `tbl_admin_session`
Enhanced session management for admin users with additional security tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Session record ID |
| `user_id` | INTEGER | NOT NULL, FK to tbl_user(id) | Admin user ID |
| `session_token` | VARCHAR(255) | UNIQUE, NOT NULL | Session token (longer for admins) |
| `expires_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | Session expiration |
| `ip_address` | VARCHAR(255) | NULL | IP address for session verification |
| `user_agent` | TEXT | NULL | Browser/client information |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Session creation time |
| `last_activity` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Last activity timestamp |

**Constraints:**
- CHECK constraint: ensures user is Admin type

**Indexes:**
- `idx_admin_session_token` on `session_token`
- `idx_admin_session_expires` on `expires_at`
- `idx_admin_session_user_id` on `user_id`
- `idx_admin_session_ip` on `ip_address`

**Relationships:**
- FK: `user_id` → `tbl_user(id)` ON DELETE CASCADE

---

### Educational Content

#### `tbl_subject`
Top-level subjects/curricula (e.g., Mathematics, Science).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Subject ID |
| `subjectname` | VARCHAR(255) | UNIQUE, NOT NULL | Subject name |
| `description` | TEXT | NULL | Subject description |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Creation timestamp |

---

#### `tbl_topic`
Topics within subjects (e.g., Algebra, Fractions).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Topic ID |
| `topicname` | VARCHAR(255) | NOT NULL | Topic name |
| `description` | TEXT | NULL | Topic description |
| `grade_level` | INTEGER | NULL | Recommended grade level |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Creation timestamp |

---

#### `tbl_topicsubject`
Many-to-many relationship between topics and subjects.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `topicid` | INTEGER | FK to tbl_topic(id) | Topic ID |
| `subjectid` | INTEGER | FK to tbl_subject(id) | Subject ID |
| `createdby` | VARCHAR(50) | NULL | Creator identifier |

**Primary Key:** Composite of `(topicid, subjectid)`

**Indexes:**
- `idx_topicsubject_topic` on `topicid`
- `idx_topicsubject_subject` on `subjectid`

**Relationships:**
- FK: `topicid` → `tbl_topic(id)` ON DELETE CASCADE
- FK: `subjectid` → `tbl_subject(id)` ON DELETE CASCADE

---

#### `tbl_question`
Questions within topics.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Question ID |
| `topicid` | INTEGER | FK to tbl_topic(id) | Associated topic |
| `questionname` | TEXT | NOT NULL | Question text |
| `questiontype` | VARCHAR(50) | NOT NULL | Question type (MultipleChoice, OpenEnded) |
| `difficultyrating` | INTEGER | CHECK (1-5) | Difficulty level 1-5 |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Creation timestamp |

**Indexes:**
- `idx_question_topic` on `topicid`

**Relationships:**
- FK: `topicid` → `tbl_topic(id)` ON DELETE CASCADE

---

#### `tbl_answer`
Answer options for questions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Answer ID |
| `questionid` | INTEGER | FK to tbl_question(id) | Associated question |
| `answername` | TEXT | NOT NULL | Answer text |
| `iscorrect` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether answer is correct |

**Indexes:**
- `idx_answer_question` on `questionid`

**Relationships:**
- FK: `questionid` → `tbl_question(id)` ON DELETE CASCADE

---

#### `tbl_step`
Solution steps for questions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Step ID |
| `questionid` | INTEGER | FK to tbl_question(id) | Associated question |
| `stepname` | TEXT | NOT NULL | Step description |
| `sequenceno` | INTEGER | NOT NULL | Step order |

**Constraints:**
- UNIQUE constraint on `(questionid, sequenceno)`

**Indexes:**
- `idx_step_question` on `questionid`

**Relationships:**
- FK: `questionid` → `tbl_question(id)` ON DELETE CASCADE

---

### Audit and Logging

#### `tbl_admin_audit_log`
Audit trail for admin actions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Log entry ID |
| `admin_user_id` | INTEGER | FK to tbl_user(id) | Admin who performed action |
| `action` | VARCHAR(100) | NOT NULL | Action performed |
| `resource_type` | VARCHAR(50) | NULL | Type of resource affected |
| `resource_id` | INTEGER | NULL | ID of affected resource |
| `details` | JSONB | NULL | Additional action details |
| `ip_address` | VARCHAR(255) | NULL | IP address of admin |
| `user_agent` | TEXT | NULL | Browser/client information |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Action timestamp |

**Indexes:**
- `idx_admin_audit_user_id` on `admin_user_id`
- `idx_admin_audit_created_at` on `created_at`
- `idx_admin_audit_action` on `action`

**Relationships:**
- FK: `admin_user_id` → `tbl_user(id)`

---

#### `migrations`
Database migration tracking (managed by migration system).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Migration record ID |
| `version` | VARCHAR(255) | UNIQUE, NOT NULL | Migration version |
| `description` | TEXT | NULL | Migration description |
| `applied_at` | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Application timestamp |
| `checksum` | VARCHAR(64) | NULL | Migration file checksum |

---

## Relationships Diagram

```
tbl_user (1) ←→ (0..1) tbl_subscription
    ↓ (1)
    ↓ 
    ↓ (0..many) tbl_user (students)
    ↓
    ↓ (1) → (0..many) tbl_user_session
    ↓ (1) → (0..many) tbl_admin_session (if Admin)
    ↓ (1) → (0..1) tbl_userpreferences

tbl_subject (1) ←→ (many) tbl_topicsubject ←→ (many) tbl_topic (1)
                                                        ↓ (1)
                                                        ↓
                                                        ↓ (0..many) tbl_question
                                                                    ↓ (1)
                                                                    ↓
                                                                    ↓ (0..many) tbl_answer
                                                                    ↓ (1)
                                                                    ↓
                                                                    ↓ (0..many) tbl_step
```

## Security Considerations

1. **Password Storage**: All passwords are hashed using bcrypt with a cost factor of 12+
2. **Session Management**: 
   - Regular users: 24-hour sessions
   - Admin users: 4-hour sessions with IP tracking
3. **Database Constraints**: Foreign key constraints ensure referential integrity
4. **Indexes**: Optimized for common query patterns
5. **Audit Logging**: All admin actions are logged for security auditing

## Migration Management

The database schema is managed through a migration system located in `/migrations/`. Each migration file is numbered sequentially and contains both schema changes and data migrations.

To run migrations:
```bash
python migration_manager.py migrate
```

To create a new migration:
```bash
python migration_manager.py create "description of changes"
```

## Performance Considerations

- Connection pooling is configured for optimal performance on Render
- Indexes are strategically placed on frequently queried columns
- CASCADE deletions ensure data consistency
- PostgreSQL-specific features (JSONB, timezone support) are utilized

## Backup and Recovery

- Regular backups should be configured through Render's PostgreSQL service
- Point-in-time recovery is available through Render's infrastructure
- Migration system allows for easy schema versioning and rollbacks