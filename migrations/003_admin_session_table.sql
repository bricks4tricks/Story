-- Migration 003: Enhanced Admin Session Table
-- Created: 2025-01-16

-- Create enhanced session table for admin users with additional security tracking
CREATE TABLE IF NOT EXISTS tbl_admin_session (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES tbl_user(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address VARCHAR(255),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT admin_user_check CHECK (
        (SELECT usertype FROM tbl_user WHERE id = user_id) = 'Admin'
    )
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_admin_session_token 
ON tbl_admin_session(session_token);

CREATE INDEX IF NOT EXISTS idx_admin_session_expires 
ON tbl_admin_session(expires_at);

CREATE INDEX IF NOT EXISTS idx_admin_session_user_id 
ON tbl_admin_session(user_id);

CREATE INDEX IF NOT EXISTS idx_admin_session_ip 
ON tbl_admin_session(ip_address);

-- Create audit log table for admin actions
CREATE TABLE IF NOT EXISTS tbl_admin_audit_log (
    id SERIAL PRIMARY KEY,
    admin_user_id INTEGER NOT NULL REFERENCES tbl_user(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    details JSONB,
    ip_address VARCHAR(255),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for audit log
CREATE INDEX IF NOT EXISTS idx_admin_audit_user_id 
ON tbl_admin_audit_log(admin_user_id);

CREATE INDEX IF NOT EXISTS idx_admin_audit_created_at 
ON tbl_admin_audit_log(created_at);

CREATE INDEX IF NOT EXISTS idx_admin_audit_action 
ON tbl_admin_audit_log(action);