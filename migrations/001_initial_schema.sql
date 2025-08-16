-- Migration 001: Initial Schema
-- Created: 2025-01-16

-- Core user management tables
CREATE TABLE IF NOT EXISTS tbl_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    passwordhash VARCHAR(255) NOT NULL,
    usertype VARCHAR(50) NOT NULL DEFAULT 'Parent',
    parentuserid INTEGER REFERENCES tbl_user(id) ON DELETE CASCADE,
    createdon TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    plan VARCHAR(20) DEFAULT 'Monthly',
    resettoken VARCHAR(255),
    resettokenexpiry TIMESTAMP WITH TIME ZONE
);

-- Subscription management
CREATE TABLE IF NOT EXISTS tbl_subscription (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES tbl_user(id) ON DELETE CASCADE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    expires_on TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User preferences
CREATE TABLE IF NOT EXISTS tbl_userpreferences (
    user_id INTEGER PRIMARY KEY REFERENCES tbl_user(id) ON DELETE CASCADE,
    darkmode BOOLEAN NOT NULL DEFAULT FALSE,
    fontsize VARCHAR(10) NOT NULL DEFAULT 'medium'
);

-- Educational content structure
CREATE TABLE IF NOT EXISTS tbl_subject (
    id SERIAL PRIMARY KEY,
    subjectname VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tbl_topic (
    id SERIAL PRIMARY KEY,
    topicname VARCHAR(255) NOT NULL,
    description TEXT,
    grade_level INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Many-to-many relationship between topics and subjects
CREATE TABLE IF NOT EXISTS tbl_topicsubject (
    topicid INTEGER REFERENCES tbl_topic(id) ON DELETE CASCADE,
    subjectid INTEGER REFERENCES tbl_subject(id) ON DELETE CASCADE,
    createdby VARCHAR(50),
    PRIMARY KEY (topicid, subjectid)
);

-- Question and answer system
CREATE TABLE IF NOT EXISTS tbl_question (
    id SERIAL PRIMARY KEY,
    topicid INTEGER REFERENCES tbl_topic(id) ON DELETE CASCADE,
    questionname TEXT NOT NULL,
    questiontype VARCHAR(50) NOT NULL,
    difficultyrating INTEGER CHECK (difficultyrating BETWEEN 1 AND 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tbl_answer (
    id SERIAL PRIMARY KEY,
    questionid INTEGER REFERENCES tbl_question(id) ON DELETE CASCADE,
    answername TEXT NOT NULL,
    iscorrect BOOLEAN NOT NULL DEFAULT FALSE
);

-- Question solving steps
CREATE TABLE IF NOT EXISTS tbl_step (
    id SERIAL PRIMARY KEY,
    questionid INTEGER REFERENCES tbl_question(id) ON DELETE CASCADE,
    stepname TEXT NOT NULL,
    sequenceno INTEGER NOT NULL,
    UNIQUE(questionid, sequenceno)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_username ON tbl_user(username);
CREATE INDEX IF NOT EXISTS idx_user_email ON tbl_user(email);
CREATE INDEX IF NOT EXISTS idx_subscription_user_id ON tbl_subscription(user_id);
CREATE INDEX IF NOT EXISTS idx_question_topic ON tbl_question(topicid);
CREATE INDEX IF NOT EXISTS idx_answer_question ON tbl_answer(questionid);
CREATE INDEX IF NOT EXISTS idx_step_question ON tbl_step(questionid);
CREATE INDEX IF NOT EXISTS idx_topicsubject_topic ON tbl_topicsubject(topicid);
CREATE INDEX IF NOT EXISTS idx_topicsubject_subject ON tbl_topicsubject(subjectid);