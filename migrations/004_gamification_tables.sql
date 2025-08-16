-- Gamification and Progress Tracking Tables
-- Phase 1 implementation for enhanced analytics

-- User points and levels tracking
CREATE TABLE IF NOT EXISTS tbl_user_gamification (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES tbl_user(id) ON DELETE CASCADE,
    total_points INTEGER NOT NULL DEFAULT 0,
    current_level INTEGER NOT NULL DEFAULT 1,
    badges_earned TEXT[] DEFAULT '{}',
    reading_streak_current INTEGER NOT NULL DEFAULT 0,
    reading_streak_longest INTEGER NOT NULL DEFAULT 0,
    last_activity_date DATE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Daily activity tracking
CREATE TABLE IF NOT EXISTS tbl_daily_activity (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES tbl_user(id) ON DELETE CASCADE,
    activity_date DATE NOT NULL,
    stories_read INTEGER NOT NULL DEFAULT 0,
    quizzes_completed INTEGER NOT NULL DEFAULT 0,
    quiz_accuracy_total INTEGER NOT NULL DEFAULT 0,
    quiz_questions_answered INTEGER NOT NULL DEFAULT 0,
    time_spent_minutes INTEGER NOT NULL DEFAULT 0,
    points_earned INTEGER NOT NULL DEFAULT 0,
    perfect_quizzes INTEGER NOT NULL DEFAULT 0,
    first_activity_time TIME,
    last_activity_time TIME,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, activity_date)
);

-- Learning session tracking
CREATE TABLE IF NOT EXISTS tbl_learning_session (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES tbl_user(id) ON DELETE CASCADE,
    session_start TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    session_end TIMESTAMP WITH TIME ZONE,
    topics_covered TEXT[],
    stories_read_ids INTEGER[],
    quizzes_taken_ids INTEGER[],
    total_questions_answered INTEGER NOT NULL DEFAULT 0,
    correct_answers INTEGER NOT NULL DEFAULT 0,
    session_type VARCHAR(50) DEFAULT 'reading', -- reading, quiz, mixed
    device_type VARCHAR(50), -- mobile, tablet, desktop
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Subject performance tracking
CREATE TABLE IF NOT EXISTS tbl_subject_performance (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES tbl_user(id) ON DELETE CASCADE,
    subject_name VARCHAR(100) NOT NULL,
    stories_completed INTEGER NOT NULL DEFAULT 0,
    quizzes_completed INTEGER NOT NULL DEFAULT 0,
    average_accuracy DECIMAL(5,2) DEFAULT 0.00,
    time_spent_minutes INTEGER NOT NULL DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE,
    proficiency_level VARCHAR(20) DEFAULT 'beginner', -- beginner, intermediate, advanced, expert
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, subject_name)
);

-- Achievement progress tracking
CREATE TABLE IF NOT EXISTS tbl_achievement_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES tbl_user(id) ON DELETE CASCADE,
    achievement_id VARCHAR(50) NOT NULL,
    progress_count INTEGER NOT NULL DEFAULT 0,
    target_count INTEGER NOT NULL,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, achievement_id)
);

-- Weekly goals and challenges
CREATE TABLE IF NOT EXISTS tbl_weekly_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES tbl_user(id) ON DELETE CASCADE,
    week_start_date DATE NOT NULL,
    goal_type VARCHAR(50) NOT NULL, -- stories_read, quiz_accuracy, time_spent
    goal_target INTEGER NOT NULL,
    current_progress INTEGER NOT NULL DEFAULT 0,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    reward_points INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, week_start_date, goal_type)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_gamification_user_id ON tbl_user_gamification(user_id);
CREATE INDEX IF NOT EXISTS idx_user_gamification_level ON tbl_user_gamification(current_level);
CREATE INDEX IF NOT EXISTS idx_user_gamification_points ON tbl_user_gamification(total_points);

CREATE INDEX IF NOT EXISTS idx_daily_activity_user_date ON tbl_daily_activity(user_id, activity_date);
CREATE INDEX IF NOT EXISTS idx_daily_activity_date ON tbl_daily_activity(activity_date);

CREATE INDEX IF NOT EXISTS idx_learning_session_user_id ON tbl_learning_session(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_session_start ON tbl_learning_session(session_start);
CREATE INDEX IF NOT EXISTS idx_learning_session_type ON tbl_learning_session(session_type);

CREATE INDEX IF NOT EXISTS idx_subject_performance_user_id ON tbl_subject_performance(user_id);
CREATE INDEX IF NOT EXISTS idx_subject_performance_subject ON tbl_subject_performance(subject_name);
CREATE INDEX IF NOT EXISTS idx_subject_performance_accuracy ON tbl_subject_performance(average_accuracy);

CREATE INDEX IF NOT EXISTS idx_achievement_progress_user_id ON tbl_achievement_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_achievement_progress_completed ON tbl_achievement_progress(is_completed);

CREATE INDEX IF NOT EXISTS idx_weekly_goals_user_week ON tbl_weekly_goals(user_id, week_start_date);
CREATE INDEX IF NOT EXISTS idx_weekly_goals_completed ON tbl_weekly_goals(is_completed);

-- Create trigger to update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables that need them
CREATE TRIGGER update_user_gamification_updated_at 
    BEFORE UPDATE ON tbl_user_gamification 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_activity_updated_at 
    BEFORE UPDATE ON tbl_daily_activity 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subject_performance_updated_at 
    BEFORE UPDATE ON tbl_subject_performance 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_achievement_progress_updated_at 
    BEFORE UPDATE ON tbl_achievement_progress 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_weekly_goals_updated_at 
    BEFORE UPDATE ON tbl_weekly_goals 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample achievement definitions
INSERT INTO tbl_achievement_progress (user_id, achievement_id, target_count)
SELECT 
    u.id,
    achievement_type.achievement_id,
    achievement_type.target_count
FROM tbl_user u
CROSS JOIN (
    VALUES 
        ('first-story', 1),
        ('bookworm', 10),
        ('scholar', 50),
        ('perfectionist', 5),
        ('speed-reader', 5),
        ('streak-master', 7),
        ('early-bird', 1),
        ('night-owl', 1)
) AS achievement_type(achievement_id, target_count)
ON CONFLICT (user_id, achievement_id) DO NOTHING;

-- Initialize gamification data for existing users
INSERT INTO tbl_user_gamification (user_id)
SELECT id FROM tbl_user
ON CONFLICT (user_id) DO NOTHING;