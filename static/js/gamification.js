/**
 * Gamification System - Badges, Points, and Achievements
 * Adds engaging game-like elements to learning experience
 */

class GamificationSystem {
    constructor() {
        this.userPoints = 0;
        this.userLevel = 1;
        this.earnedBadges = [];
        this.achievements = this.defineAchievements();
        this.pointsConfig = {
            storyRead: 10,
            quizCompleted: 15,
            perfectQuiz: 25,
            dailyStreak: 5,
            weeklyGoal: 50
        };
    }

    /**
     * Define all available achievements and badges
     */
    defineAchievements() {
        return {
            badges: {
                firstStory: {
                    id: 'first-story',
                    name: 'First Steps',
                    description: 'Read your first story',
                    icon: '📖',
                    color: '#10b981',
                    requirement: { type: 'stories_read', count: 1 }
                },
                bookworm: {
                    id: 'bookworm',
                    name: 'Bookworm',
                    description: 'Read 10 stories',
                    icon: '🐛',
                    color: '#3b82f6',
                    requirement: { type: 'stories_read', count: 10 }
                },
                scholar: {
                    id: 'scholar',
                    name: 'Scholar',
                    description: 'Read 50 stories',
                    icon: '🎓',
                    color: '#8b5cf6',
                    requirement: { type: 'stories_read', count: 50 }
                },
                perfectionist: {
                    id: 'perfectionist',
                    name: 'Perfectionist',
                    description: 'Get 100% on 5 quizzes',
                    icon: '💯',
                    color: '#f59e0b',
                    requirement: { type: 'perfect_quizzes', count: 5 }
                },
                speedReader: {
                    id: 'speed-reader',
                    name: 'Speed Reader',
                    description: 'Read 5 stories in one day',
                    icon: '⚡',
                    color: '#ef4444',
                    requirement: { type: 'daily_stories', count: 5 }
                },
                streakMaster: {
                    id: 'streak-master',
                    name: 'Streak Master',
                    description: 'Read for 7 days in a row',
                    icon: '🔥',
                    color: '#f97316',
                    requirement: { type: 'reading_streak', count: 7 }
                },
                earlyBird: {
                    id: 'early-bird',
                    name: 'Early Bird',
                    description: 'Read before 9 AM',
                    icon: '🌅',
                    color: '#06b6d4',
                    requirement: { type: 'early_reading', count: 1 }
                },
                nightOwl: {
                    id: 'night-owl',
                    name: 'Night Owl',
                    description: 'Read after 9 PM',
                    icon: '🦉',
                    color: '#6366f1',
                    requirement: { type: 'late_reading', count: 1 }
                }
            },
            levels: [
                { level: 1, pointsRequired: 0, title: 'Beginner Reader', icon: '🌱' },
                { level: 2, pointsRequired: 100, title: 'Story Explorer', icon: '🗺️' },
                { level: 3, pointsRequired: 250, title: 'Book Adventurer', icon: '⛰️' },
                { level: 4, pointsRequired: 500, title: 'Reading Champion', icon: '🏆' },
                { level: 5, pointsRequired: 1000, title: 'Literature Master', icon: '👑' }
            ]
        };
    }

    /**
     * Initialize gamification system
     */
    async initialize() {
        try {
            await this.loadUserProgress();
            this.createProgressDisplay();
            this.createBadgeDisplay();
            this.setupEventListeners();
        } catch (error) {
            console.error('Error initializing gamification:', error);
        }
    }

    /**
     * Load user's current progress from server
     */
    async loadUserProgress() {
        const response = await csrfManager.get('/api/gamification/progress');
        if (response.ok) {
            const data = await response.json();
            this.userPoints = data.points || 0;
            this.userLevel = data.level || 1;
            this.earnedBadges = data.badges || [];
        }
    }

    /**
     * Award points for various actions
     */
    async awardPoints(action, amount = null) {
        const points = amount || this.pointsConfig[action] || 0;
        if (points <= 0) return;

        this.userPoints += points;
        
        // Show points animation
        this.showPointsAnimation(points);
        
        // Check for level up
        this.checkLevelUp();
        
        // Update server
        await this.updateServerProgress();
        
        // Update display
        this.updateProgressDisplay();
    }

    /**
     * Check and award badges based on achievements
     */
    async checkBadgeProgress(actionType, data = {}) {
        const newBadges = [];
        
        Object.values(this.achievements.badges).forEach(badge => {
            if (!this.earnedBadges.includes(badge.id)) {
                if (this.meetsBadgeRequirement(badge, actionType, data)) {
                    newBadges.push(badge);
                    this.earnedBadges.push(badge.id);
                }
            }
        });
        
        if (newBadges.length > 0) {
            await this.updateServerProgress();
            this.showBadgeNotifications(newBadges);
            this.updateBadgeDisplay();
        }
    }

    /**
     * Check if user meets badge requirement
     */
    meetsBadgeRequirement(badge, actionType, data) {
        const req = badge.requirement;
        
        switch (req.type) {
            case 'stories_read':
                return data.totalStoriesRead >= req.count;
            case 'perfect_quizzes':
                return data.perfectQuizzes >= req.count;
            case 'daily_stories':
                return data.storiesReadToday >= req.count;
            case 'reading_streak':
                return data.currentStreak >= req.count;
            case 'early_reading':
                return data.isEarlyReading;
            case 'late_reading':
                return data.isLateReading;
            default:
                return false;
        }
    }

    /**
     * Check for level up
     */
    checkLevelUp() {
        const currentLevel = this.getCurrentLevel();
        if (currentLevel.level > this.userLevel) {
            this.userLevel = currentLevel.level;
            this.showLevelUpNotification(currentLevel);
        }
    }

    /**
     * Get current level based on points
     */
    getCurrentLevel() {
        const levels = this.achievements.levels;
        for (let i = levels.length - 1; i >= 0; i--) {
            if (this.userPoints >= levels[i].pointsRequired) {
                return levels[i];
            }
        }
        return levels[0];
    }

    /**
     * Create progress display widget
     */
    createProgressDisplay() {
        const container = document.getElementById('gamification-progress');
        if (!container) return;

        const currentLevel = this.getCurrentLevel();
        const nextLevel = this.achievements.levels.find(l => l.level === this.userLevel + 1);
        const progressPercent = nextLevel ? 
            ((this.userPoints - currentLevel.pointsRequired) / 
             (nextLevel.pointsRequired - currentLevel.pointsRequired)) * 100 : 100;

        const progressWidget = SecureDOM.createElement('div', {
            className: 'bg-slate-800 rounded-lg p-6 border border-slate-700'
        });

        const header = SecureDOM.createElement('div', {
            className: 'flex items-center justify-between mb-4'
        });

        const levelInfo = SecureDOM.createElement('div', {
            className: 'flex items-center space-x-2'
        });
        
        const levelIcon = SecureDOM.createElement('span', {
            className: 'text-2xl'
        }, currentLevel.icon);
        
        const levelText = SecureDOM.createElement('div');
        const levelTitle = SecureDOM.createElement('h3', {
            className: 'text-white font-bold'
        }, `Level ${currentLevel.level}`);
        const levelName = SecureDOM.createElement('p', {
            className: 'text-gray-400 text-sm'
        }, currentLevel.title);
        
        SecureDOM.appendContent(levelText, levelTitle, levelName);
        SecureDOM.appendContent(levelInfo, levelIcon, levelText);
        
        const pointsDisplay = SecureDOM.createElement('div', {
            className: 'text-right'
        });
        const pointsText = SecureDOM.createElement('div', {
            className: 'text-2xl font-bold text-yellow-400'
        }, `${this.userPoints}`);
        const pointsLabel = SecureDOM.createElement('div', {
            className: 'text-gray-400 text-sm'
        }, 'Points');
        
        SecureDOM.appendContent(pointsDisplay, pointsText, pointsLabel);
        SecureDOM.appendContent(header, levelInfo, pointsDisplay);
        
        // Progress bar
        const progressBar = SecureDOM.createElement('div', {
            className: 'w-full bg-slate-700 rounded-full h-3 mb-2'
        });
        const progressFill = SecureDOM.createElement('div', {
            className: 'bg-blue-500 h-3 rounded-full transition-all duration-500',
            style: { width: `${Math.min(progressPercent, 100)}%` }
        });
        progressBar.appendChild(progressFill);
        
        const progressText = SecureDOM.createElement('div', {
            className: 'text-gray-400 text-sm text-center'
        }, nextLevel ? 
            `${nextLevel.pointsRequired - this.userPoints} points to ${nextLevel.title}` : 
            'Max level reached!'
        );
        
        SecureDOM.appendContent(progressWidget, header, progressBar, progressText);
        SecureDOM.replaceContent(container, progressWidget);
    }

    /**
     * Create badge display
     */
    createBadgeDisplay() {
        const container = document.getElementById('badges-container');
        if (!container) return;

        SecureDOM.replaceContent(container);
        
        const badgeGrid = SecureDOM.createElement('div', {
            className: 'grid grid-cols-2 md:grid-cols-4 gap-4'
        });

        Object.values(this.achievements.badges).forEach(badge => {
            const isEarned = this.earnedBadges.includes(badge.id);
            const badgeCard = this.createBadgeCard(badge, isEarned);
            badgeGrid.appendChild(badgeCard);
        });

        container.appendChild(badgeGrid);
    }

    /**
     * Create individual badge card
     */
    createBadgeCard(badge, isEarned) {
        const card = SecureDOM.createElement('div', {
            className: `relative p-4 rounded-lg border-2 text-center transition-all duration-300 ${
                isEarned 
                    ? 'bg-slate-800 border-slate-600 shadow-lg' 
                    : 'bg-slate-900 border-slate-700 opacity-50'
            }`
        });

        const icon = SecureDOM.createElement('div', {
            className: `text-4xl mb-2 ${isEarned ? '' : 'grayscale'}`
        }, badge.icon);

        const name = SecureDOM.createElement('h4', {
            className: `font-semibold text-white mb-1 ${isEarned ? '' : 'text-gray-500'}`
        }, badge.name);

        const description = SecureDOM.createElement('p', {
            className: `text-xs ${isEarned ? 'text-gray-300' : 'text-gray-600'}`
        }, badge.description);

        if (isEarned) {
            const earnedBadge = SecureDOM.createElement('div', {
                className: 'absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full'
            }, '✓');
            card.appendChild(earnedBadge);
        }

        SecureDOM.appendContent(card, icon, name, description);
        return card;
    }

    /**
     * Show points animation
     */
    showPointsAnimation(points) {
        const animation = SecureDOM.createElement('div', {
            className: 'fixed top-20 right-4 z-50 bg-yellow-500 text-black px-4 py-2 rounded-lg font-bold shadow-lg transform transition-all duration-1000',
            style: { transform: 'translateY(0px)', opacity: '1' }
        }, `+${points} points!`);

        document.body.appendChild(animation);

        SecureDOM.safeTimeout(() => {
            animation.style.transform = 'translateY(-50px)';
            animation.style.opacity = '0';
        }, 100);

        SecureDOM.safeTimeout(() => {
            document.body.removeChild(animation);
        }, 1100);
    }

    /**
     * Show badge notification
     */
    showBadgeNotifications(badges) {
        badges.forEach((badge, index) => {
            SecureDOM.safeTimeout(() => {
                this.showBadgeNotification(badge);
            }, index * 500);
        });
    }

    /**
     * Show individual badge notification
     */
    showBadgeNotification(badge) {
        const notification = SecureDOM.createElement('div', {
            className: 'fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 bg-slate-800 border-2 border-yellow-400 rounded-lg p-6 text-center shadow-2xl max-w-sm'
        });

        const title = SecureDOM.createElement('h3', {
            className: 'text-yellow-400 font-bold text-xl mb-2'
        }, 'Badge Earned!');

        const icon = SecureDOM.createElement('div', {
            className: 'text-6xl mb-4'
        }, badge.icon);

        const name = SecureDOM.createElement('h4', {
            className: 'text-white font-semibold text-lg mb-2'
        }, badge.name);

        const description = SecureDOM.createElement('p', {
            className: 'text-gray-300'
        }, badge.description);

        const closeBtn = SecureDOM.createElement('button', {
            className: 'mt-4 bg-yellow-400 text-black px-4 py-2 rounded font-semibold hover:bg-yellow-300 transition-colors'
        }, 'Awesome!');

        closeBtn.addEventListener('click', () => {
            document.body.removeChild(notification);
        });

        SecureDOM.appendContent(notification, title, icon, name, description, closeBtn);
        document.body.appendChild(notification);

        // Auto-close after 5 seconds
        SecureDOM.safeTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 5000);
    }

    /**
     * Show level up notification
     */
    showLevelUpNotification(level) {
        const notification = SecureDOM.createElement('div', {
            className: 'fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-8 text-center shadow-2xl max-w-md border-2 border-white'
        });

        const title = SecureDOM.createElement('h3', {
            className: 'text-white font-bold text-2xl mb-4'
        }, 'LEVEL UP!');

        const icon = SecureDOM.createElement('div', {
            className: 'text-8xl mb-4'
        }, level.icon);

        const levelInfo = SecureDOM.createElement('div', {
            className: 'text-white mb-4'
        });

        const levelNumber = SecureDOM.createElement('div', {
            className: 'text-4xl font-bold'
        }, `Level ${level.level}`);

        const levelTitle = SecureDOM.createElement('div', {
            className: 'text-xl'
        }, level.title);

        SecureDOM.appendContent(levelInfo, levelNumber, levelTitle);

        const closeBtn = SecureDOM.createElement('button', {
            className: 'mt-4 bg-white text-purple-600 px-6 py-3 rounded-full font-bold hover:bg-gray-100 transition-colors'
        }, 'Continue Reading!');

        closeBtn.addEventListener('click', () => {
            document.body.removeChild(notification);
        });

        SecureDOM.appendContent(notification, title, icon, levelInfo, closeBtn);
        document.body.appendChild(notification);

        // Auto-close after 8 seconds
        SecureDOM.safeTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 8000);
    }

    /**
     * Update progress display
     */
    updateProgressDisplay() {
        this.createProgressDisplay();
    }

    /**
     * Update badge display
     */
    updateBadgeDisplay() {
        this.createBadgeDisplay();
    }

    /**
     * Update server with current progress
     */
    async updateServerProgress() {
        try {
            await csrfManager.post('/api/gamification/progress', {
                points: this.userPoints,
                level: this.userLevel,
                badges: this.earnedBadges
            });
        } catch (error) {
            console.error('Error updating gamification progress:', error);
        }
    }

    /**
     * Setup event listeners for gamification triggers
     */
    setupEventListeners() {
        // Listen for story completion events
        document.addEventListener('storyCompleted', (event) => {
            this.awardPoints('storyRead');
            this.checkBadgeProgress('story_read', event.detail);
        });

        // Listen for quiz completion events
        document.addEventListener('quizCompleted', (event) => {
            const points = event.detail.perfect ? 'perfectQuiz' : 'quizCompleted';
            this.awardPoints(points);
            this.checkBadgeProgress('quiz_completed', event.detail);
        });

        // Listen for streak events
        document.addEventListener('streakUpdated', (event) => {
            this.awardPoints('dailyStreak');
            this.checkBadgeProgress('streak_updated', event.detail);
        });
    }
}

// Initialize gamification system only on appropriate pages
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize gamification on dashboard, settings, and story pages
    const currentPath = window.location.pathname;
    const allowedPaths = ['/dashboard.html', '/settings.html', '/story-player.html'];
    const isAllowedPage = allowedPaths.some(path => currentPath.includes(path)) || 
                         currentPath === '/' && document.getElementById('gamification-progress'); // Only if gamification elements exist
    
    if (isAllowedPage) {
        window.gamificationSystem = new GamificationSystem();
        window.gamificationSystem.initialize();
    }
});

// Export for use in other modules
window.GamificationSystem = GamificationSystem;