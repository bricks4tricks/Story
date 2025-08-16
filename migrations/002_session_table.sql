-- Migration 002: Session Management Table
-- Created: 2025-01-16

-- Create session management table for token-based authentication
CREATE TABLE IF NOT EXISTS tbl_user_session (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES tbl_user(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    user_type VARCHAR(20) NOT NULL DEFAULT 'student',
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_session_token 
ON tbl_user_session(session_token);

CREATE INDEX IF NOT EXISTS idx_user_session_expires 
ON tbl_user_session(expires_at);

CREATE INDEX IF NOT EXISTS idx_user_session_user_id 
ON tbl_user_session(user_id);