/**
 * Progress Visualization with Chart.js
 * Provides interactive charts for learning analytics
 */

class ProgressCharts {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: '#3b82f6',
            success: '#10b981',
            warning: '#f59e0b',
            danger: '#ef4444',
            info: '#06b6d4',
            gradient: {
                start: '#3b82f6',
                end: '#1d4ed8'
            }
        };
    }

    /**
     * Create gradient background for charts
     */
    createGradient(ctx, startColor, endColor) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, startColor);
        gradient.addColorStop(1, endColor);
        return gradient;
    }

    /**
     * Initialize all progress charts
     */
    async initializeCharts() {
        try {
            const progressData = await this.fetchProgressData();
            
            this.createWeeklyProgressChart(progressData.weeklyProgress);
            this.createSubjectPerformanceChart(progressData.subjectPerformance);
            this.createStreakChart(progressData.streakData);
            this.createAccuracyTrendChart(progressData.accuracyTrend);
            
        } catch (error) {
            console.error('Error initializing charts:', error);
            this.showChartError();
        }
    }

    /**
     * Fetch progress data from API
     */
    async fetchProgressData() {
        const response = await csrfManager.get('/api/progress/analytics');
        if (!response.ok) {
            throw new Error('Failed to fetch progress data');
        }
        return await response.json();
    }

    /**
     * Weekly Progress Line Chart
     */
    createWeeklyProgressChart(data) {
        const ctx = document.getElementById('weeklyProgressChart');
        if (!ctx) return;

        const gradient = this.createGradient(ctx.getContext('2d'), 
            this.colors.gradient.start + '80', 
            this.colors.gradient.end + '20'
        );

        this.charts.weeklyProgress = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Stories Completed',
                    data: data.storiesCompleted,
                    borderColor: this.colors.primary,
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: this.colors.primary,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: this.colors.primary,
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#6b7280'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#374151',
                            borderDash: [2, 2]
                        },
                        ticks: {
                            color: '#6b7280'
                        }
                    }
                },
                elements: {
                    point: {
                        hoverBackgroundColor: this.colors.primary
                    }
                }
            }
        });
    }

    /**
     * Subject Performance Doughnut Chart
     */
    createSubjectPerformanceChart(data) {
        const ctx = document.getElementById('subjectPerformanceChart');
        if (!ctx) return;

        this.charts.subjectPerformance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.subjects,
                datasets: [{
                    data: data.scores,
                    backgroundColor: [
                        this.colors.primary,
                        this.colors.success,
                        this.colors.warning,
                        this.colors.info,
                        this.colors.danger
                    ],
                    borderWidth: 3,
                    borderColor: '#1f2937',
                    hoverBorderWidth: 4,
                    hoverBorderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#d1d5db',
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: this.colors.primary,
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed * 100) / total).toFixed(1);
                                return `${context.label}: ${percentage}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * Reading Streak Bar Chart
     */
    createStreakChart(data) {
        const ctx = document.getElementById('streakChart');
        if (!ctx) return;

        this.charts.streak = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.days,
                datasets: [{
                    label: 'Reading Streak',
                    data: data.streakCounts,
                    backgroundColor: data.streakCounts.map(count => 
                        count > 0 ? this.colors.success : '#374151'
                    ),
                    borderRadius: 4,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: this.colors.success,
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                return context.parsed.y > 0 ? 
                                    `${context.parsed.y} stories read` : 
                                    'No reading activity';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#6b7280'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#374151',
                            borderDash: [2, 2]
                        },
                        ticks: {
                            color: '#6b7280',
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    /**
     * Accuracy Trend Area Chart
     */
    createAccuracyTrendChart(data) {
        const ctx = document.getElementById('accuracyTrendChart');
        if (!ctx) return;

        const gradient = this.createGradient(ctx.getContext('2d'), 
            this.colors.success + '60', 
            this.colors.success + '10'
        );

        this.charts.accuracyTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [{
                    label: 'Quiz Accuracy %',
                    data: data.accuracyPercentages,
                    borderColor: this.colors.success,
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: this.colors.success,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: this.colors.success,
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                return `Accuracy: ${context.parsed.y}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#6b7280'
                        }
                    },
                    y: {
                        min: 0,
                        max: 100,
                        grid: {
                            color: '#374151',
                            borderDash: [2, 2]
                        },
                        ticks: {
                            color: '#6b7280',
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * Show error state for charts
     */
    showChartError() {
        const chartContainers = document.querySelectorAll('.chart-container');
        chartContainers.forEach(container => {
            SecureDOM.setErrorState(container, 'Unable to load chart data');
        });
    }

    /**
     * Refresh all charts with new data
     */
    async refreshCharts() {
        try {
            const progressData = await this.fetchProgressData();
            
            Object.keys(this.charts).forEach(chartKey => {
                if (this.charts[chartKey]) {
                    this.charts[chartKey].destroy();
                }
            });
            
            await this.initializeCharts();
        } catch (error) {
            console.error('Error refreshing charts:', error);
        }
    }

    /**
     * Destroy all charts (cleanup)
     */
    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if Chart.js is loaded
    if (typeof Chart !== 'undefined') {
        window.progressCharts = new ProgressCharts();
        window.progressCharts.initializeCharts();
    } else {
        console.warn('Chart.js not loaded - progress charts unavailable');
    }
});

// Export for use in other modules
window.ProgressCharts = ProgressCharts;