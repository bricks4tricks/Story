-- Migration 005: Missing Content Tables
-- Created: 2025-01-30
-- Adds tables referenced by the application but not in previous migrations

-- Lesson system (links curriculum with units and topics)
CREATE TABLE IF NOT EXISTS tbl_lesson (
    id SERIAL PRIMARY KEY,
    lesson_name VARCHAR(255) NOT NULL,
    unit_name VARCHAR(255) NOT NULL,
    grade_name VARCHAR(100) NOT NULL,
    curriculum_id INTEGER REFERENCES tbl_subject(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Video content for topics
CREATE TABLE IF NOT EXISTS tbl_video (
    id SERIAL PRIMARY KEY,
    topicid INTEGER REFERENCES tbl_topic(id) ON DELETE CASCADE,
    youtubeurl VARCHAR(500) NOT NULL,
    title VARCHAR(255),
    description TEXT,
    duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Story content for topics
CREATE TABLE IF NOT EXISTS tbl_story (
    id SERIAL PRIMARY KEY,
    topicid INTEGER REFERENCES tbl_topic(id) ON DELETE CASCADE,
    story TEXT NOT NULL,
    title VARCHAR(255),
    reading_level INTEGER CHECK (reading_level BETWEEN 1 AND 12),
    word_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quiz results tracking
CREATE TABLE IF NOT EXISTS tbl_quiz_result (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES tbl_user(id) ON DELETE CASCADE,
    topic_id INTEGER REFERENCES tbl_topic(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    questions_answered INTEGER NOT NULL DEFAULT 0,
    questions_correct INTEGER NOT NULL DEFAULT 0,
    time_taken_seconds INTEGER,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Flagging system for reporting issues
CREATE TABLE IF NOT EXISTS tbl_flag (
    id SERIAL PRIMARY KEY,
    flagid SERIAL UNIQUE,
    item_type VARCHAR(50) NOT NULL, -- 'Question', 'Story', 'Page', etc.
    item_id INTEGER, -- Reference to the flagged item
    item_name VARCHAR(255),
    description TEXT NOT NULL,
    page_path VARCHAR(500), -- For page errors
    status VARCHAR(20) NOT NULL DEFAULT 'open', -- 'open', 'Pending', 'Reviewed', 'Dismissed'
    flagged_by_user_id INTEGER REFERENCES tbl_user(id) ON DELETE SET NULL,
    reviewed_by_admin_id INTEGER REFERENCES tbl_user(id) ON DELETE SET NULL,
    flagged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    admin_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Question attempt tracking (separate from quiz results)
CREATE TABLE IF NOT EXISTS tbl_question_attempt (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES tbl_user(id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES tbl_question(id) ON DELETE CASCADE,
    user_answer TEXT,
    is_correct BOOLEAN NOT NULL,
    difficulty_at_attempt INTEGER CHECK (difficulty_at_attempt BETWEEN 1 AND 5),
    time_taken_seconds INTEGER,
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_lesson_curriculum ON tbl_lesson(curriculum_id);
CREATE INDEX IF NOT EXISTS idx_lesson_grade ON tbl_lesson(grade_name);
CREATE INDEX IF NOT EXISTS idx_lesson_unit ON tbl_lesson(unit_name);

CREATE INDEX IF NOT EXISTS idx_video_topic ON tbl_video(topicid);
CREATE INDEX IF NOT EXISTS idx_video_url ON tbl_video(youtubeurl);

CREATE INDEX IF NOT EXISTS idx_story_topic ON tbl_story(topicid);
CREATE INDEX IF NOT EXISTS idx_story_reading_level ON tbl_story(reading_level);

CREATE INDEX IF NOT EXISTS idx_quiz_result_user ON tbl_quiz_result(user_id);
CREATE INDEX IF NOT EXISTS idx_quiz_result_topic ON tbl_quiz_result(topic_id);
CREATE INDEX IF NOT EXISTS idx_quiz_result_score ON tbl_quiz_result(score);
CREATE INDEX IF NOT EXISTS idx_quiz_result_completed ON tbl_quiz_result(completed_at);

CREATE INDEX IF NOT EXISTS idx_flag_status ON tbl_flag(status);
CREATE INDEX IF NOT EXISTS idx_flag_type ON tbl_flag(item_type);
CREATE INDEX IF NOT EXISTS idx_flag_item ON tbl_flag(item_type, item_id);
CREATE INDEX IF NOT EXISTS idx_flag_flagged_by ON tbl_flag(flagged_by_user_id);
CREATE INDEX IF NOT EXISTS idx_flag_reviewed_by ON tbl_flag(reviewed_by_admin_id);

CREATE INDEX IF NOT EXISTS idx_question_attempt_user ON tbl_question_attempt(user_id);
CREATE INDEX IF NOT EXISTS idx_question_attempt_question ON tbl_question_attempt(question_id);
CREATE INDEX IF NOT EXISTS idx_question_attempt_correct ON tbl_question_attempt(is_correct);
CREATE INDEX IF NOT EXISTS idx_question_attempt_attempted ON tbl_question_attempt(attempted_at);

-- Progress tracking tables
CREATE TABLE IF NOT EXISTS tbl_story_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES tbl_user(id) ON DELETE CASCADE,
    story_id INTEGER REFERENCES tbl_story(id) ON DELETE CASCADE,
    topic_id INTEGER REFERENCES tbl_topic(id) ON DELETE CASCADE,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    time_spent_seconds INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, story_id)
);

CREATE TABLE IF NOT EXISTS tbl_video_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES tbl_user(id) ON DELETE CASCADE,
    video_id INTEGER REFERENCES tbl_video(id) ON DELETE CASCADE,
    topic_id INTEGER REFERENCES tbl_topic(id) ON DELETE CASCADE,
    watched BOOLEAN NOT NULL DEFAULT FALSE,
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    time_watched_seconds INTEGER DEFAULT 0,
    last_position_seconds INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, video_id)
);

-- Create indexes for progress tracking tables
CREATE INDEX IF NOT EXISTS idx_story_progress_user ON tbl_story_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_story_progress_story ON tbl_story_progress(story_id);
CREATE INDEX IF NOT EXISTS idx_story_progress_completed ON tbl_story_progress(completed);

CREATE INDEX IF NOT EXISTS idx_video_progress_user ON tbl_video_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_video_progress_video ON tbl_video_progress(video_id);
CREATE INDEX IF NOT EXISTS idx_video_progress_watched ON tbl_video_progress(watched);

-- Create triggers for updated_at timestamps (reusing function from 004)
CREATE TRIGGER update_lesson_updated_at 
    BEFORE UPDATE ON tbl_lesson 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_video_updated_at 
    BEFORE UPDATE ON tbl_video 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_story_updated_at 
    BEFORE UPDATE ON tbl_story 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_flag_updated_at 
    BEFORE UPDATE ON tbl_flag 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_story_progress_updated_at 
    BEFORE UPDATE ON tbl_story_progress 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_video_progress_updated_at 
    BEFORE UPDATE ON tbl_video_progress 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();