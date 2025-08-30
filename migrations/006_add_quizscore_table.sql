-- Migration 006: Add missing tbl_quizscore table
-- Created: 2025-01-30
-- Adds the tbl_quizscore table referenced by quiz result endpoints

-- Quiz score tracking (matches original app.py expectations)
CREATE TABLE IF NOT EXISTS tbl_quizscore (
    id SERIAL PRIMARY KEY,
    userid INTEGER REFERENCES tbl_user(id) ON DELETE CASCADE,
    topicid INTEGER REFERENCES tbl_topic(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    takenon TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_quizscore_user ON tbl_quizscore(userid);
CREATE INDEX IF NOT EXISTS idx_quizscore_topic ON tbl_quizscore(topicid);
CREATE INDEX IF NOT EXISTS idx_quizscore_score ON tbl_quizscore(score);
CREATE INDEX IF NOT EXISTS idx_quizscore_taken ON tbl_quizscore(takenon);