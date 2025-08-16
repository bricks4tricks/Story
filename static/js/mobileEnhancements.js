/**
 * Mobile Enhancement Utilities
 * Provides touch gestures, haptic feedback, and mobile-specific interactions
 */

class MobileEnhancements {
    constructor() {
        this.isTouch = 'ontouchstart' in window;
        this.isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        this.isAndroid = /Android/.test(navigator.userAgent);
        this.touchStartTime = 0;
        this.touchEndTime = 0;
        this.swipeThreshold = 50;
        this.tapThreshold = 200;
        
        this.init();
    }

    /**
     * Initialize mobile enhancements
     */
    init() {
        if (this.isTouch) {
            this.addTouchClasses();
            this.setupSwipeGestures();
            this.setupPullToRefresh();
            this.setupTouchFeedback();
            this.setupBottomSheet();
            this.optimizeScrolling();
            this.handleIOSViewport();
        }
        
        this.setupResponsiveImages();
        this.setupProgressiveLoading();
    }

    /**
     * Add touch-specific CSS classes
     */
    addTouchClasses() {
        document.documentElement.classList.add('touch-device');
        if (this.isIOS) document.documentElement.classList.add('ios');
        if (this.isAndroid) document.documentElement.classList.add('android');
    }

    /**
     * Setup swipe gesture detection
     */
    setupSwipeGestures() {
        let startX, startY, startTime;
        
        document.addEventListener('touchstart', (e) => {
            const touch = e.touches[0];
            startX = touch.clientX;
            startY = touch.clientY;
            startTime = Date.now();
        }, { passive: true });
        
        document.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;
            
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            const endTime = Date.now();
            
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            const deltaTime = endTime - startTime;
            
            // Detect swipe direction
            if (Math.abs(deltaX) > this.swipeThreshold || Math.abs(deltaY) > this.swipeThreshold) {
                if (deltaTime < 500) { // Quick swipe
                    this.handleSwipe(deltaX, deltaY, e.target);
                }
            }
            
            // Reset
            startX = startY = null;
        }, { passive: true });
    }

    /**
     * Handle swipe gestures
     */
    handleSwipe(deltaX, deltaY, target) {
        const direction = Math.abs(deltaX) > Math.abs(deltaY) ? 
            (deltaX > 0 ? 'right' : 'left') : 
            (deltaY > 0 ? 'down' : 'up');
        
        // Dispatch custom swipe event
        const swipeEvent = new CustomEvent('swipe', {
            detail: { direction, deltaX, deltaY, target }
        });
        
        target.dispatchEvent(swipeEvent);
        
        // Handle specific swipe actions
        this.handleSwipeActions(direction, target);
    }

    /**
     * Handle specific swipe actions
     */
    handleSwipeActions(direction, target) {
        // Swipe left on cards to show more options
        if (direction === 'left' && target.closest('.swipeable-card')) {
            this.showCardActions(target.closest('.swipeable-card'));
        }
        
        // Swipe right to go back
        if (direction === 'right' && window.location.pathname !== '/') {
            this.addSwipeIndicator();
            // Debounced back navigation
            this.debounce(() => {
                if (window.history.length > 1) {
                    window.history.back();
                }
            }, 300)();
        }
        
        // Swipe down to refresh (if at top of page)
        if (direction === 'down' && window.scrollY === 0) {
            this.triggerPullRefresh();
        }
    }

    /**
     * Setup pull-to-refresh functionality
     */
    setupPullToRefresh() {
        let startY = 0;
        let currentY = 0;
        let isPulling = false;
        const refreshThreshold = 80;
        
        const refreshIndicator = SecureDOM.createElement('div', {
            className: 'refresh-indicator',
            id: 'refresh-indicator'
        }, '↓ Pull to refresh');
        
        document.body.appendChild(refreshIndicator);
        
        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
            }
        }, { passive: true });
        
        document.addEventListener('touchmove', (e) => {
            if (window.scrollY === 0 && startY) {
                currentY = e.touches[0].clientY;
                const pullDistance = currentY - startY;
                
                if (pullDistance > 0) {
                    isPulling = true;
                    const progress = Math.min(pullDistance / refreshThreshold, 1);
                    
                    if (progress > 0.5) {
                        refreshIndicator.classList.add('visible');
                        refreshIndicator.textContent = pullDistance > refreshThreshold ? 
                            '↑ Release to refresh' : '↓ Pull to refresh';
                    } else {
                        refreshIndicator.classList.remove('visible');
                    }
                }
            }
        }, { passive: true });
        
        document.addEventListener('touchend', () => {
            if (isPulling) {
                const pullDistance = currentY - startY;
                
                if (pullDistance > refreshThreshold) {
                    this.triggerPullRefresh();
                }
                
                refreshIndicator.classList.remove('visible');
                isPulling = false;
                startY = currentY = 0;
            }
        }, { passive: true });
    }

    /**
     * Trigger pull-to-refresh action
     */
    triggerPullRefresh() {
        const refreshIndicator = document.getElementById('refresh-indicator');
        if (refreshIndicator) {
            refreshIndicator.textContent = 'Refreshing...';
            refreshIndicator.classList.add('visible');
        }
        
        // Dispatch refresh event
        document.dispatchEvent(new CustomEvent('pullRefresh'));
        
        // Simulate refresh delay
        SecureDOM.safeTimeout(() => {
            if (refreshIndicator) {
                refreshIndicator.classList.remove('visible');
            }
            window.location.reload();
        }, 1000);
    }

    /**
     * Setup haptic-like touch feedback
     */
    setupTouchFeedback() {
        // Add touch feedback to interactive elements
        const interactiveElements = document.querySelectorAll(
            'button, .touch-target, .mobile-card, a, [role="button"]'
        );
        
        interactiveElements.forEach(element => {
            element.addEventListener('touchstart', () => {
                this.addHapticFeedback(element, 'light');
            }, { passive: true });
        });
        
        // Special feedback for important actions
        const importantElements = document.querySelectorAll(
            '.mobile-button, .fab, [data-haptic="medium"]'
        );
        
        importantElements.forEach(element => {
            element.addEventListener('touchstart', () => {
                this.addHapticFeedback(element, 'medium');
            }, { passive: true });
        });
    }

    /**
     * Add visual haptic feedback
     */
    addHapticFeedback(element, intensity = 'light') {
        // Try native haptic feedback first (iOS/Android)
        if (navigator.vibrate) {
            const patterns = {
                light: [10],
                medium: [20],
                heavy: [30, 10, 30]
            };
            navigator.vibrate(patterns[intensity] || patterns.light);
        }
        
        // Visual feedback
        element.classList.add(`haptic-${intensity}`);
        SecureDOM.safeTimeout(() => {
            element.classList.remove(`haptic-${intensity}`);
        }, intensity === 'heavy' ? 200 : intensity === 'medium' ? 150 : 100);
    }

    /**
     * Setup bottom sheet component
     */
    setupBottomSheet() {
        // Create bottom sheet container if it doesn't exist
        let bottomSheet = document.getElementById('bottom-sheet');
        if (!bottomSheet) {
            bottomSheet = SecureDOM.createElement('div', {
                className: 'bottom-sheet',
                id: 'bottom-sheet'
            });
            
            const handle = SecureDOM.createElement('div', {
                className: 'bottom-sheet-handle'
            });
            
            const content = SecureDOM.createElement('div', {
                className: 'bottom-sheet-content',
                id: 'bottom-sheet-content'
            });
            
            SecureDOM.appendContent(bottomSheet, handle, content);
            document.body.appendChild(bottomSheet);
            
            // Handle swipe to close
            handle.addEventListener('touchstart', this.handleBottomSheetSwipe.bind(this));
        }
    }

    /**
     * Show bottom sheet with content
     */
    showBottomSheet(content) {
        const bottomSheet = document.getElementById('bottom-sheet');
        const bottomSheetContent = document.getElementById('bottom-sheet-content');
        
        if (bottomSheet && bottomSheetContent) {
            SecureDOM.replaceContent(bottomSheetContent, content);
            bottomSheet.classList.add('active');
            
            // Add backdrop
            const backdrop = SecureDOM.createElement('div', {
                className: 'mobile-menu-overlay active',
                id: 'bottom-sheet-backdrop'
            });
            
            backdrop.addEventListener('click', () => {
                this.hideBottomSheet();
            });
            
            document.body.appendChild(backdrop);
        }
    }

    /**
     * Hide bottom sheet
     */
    hideBottomSheet() {
        const bottomSheet = document.getElementById('bottom-sheet');
        const backdrop = document.getElementById('bottom-sheet-backdrop');
        
        if (bottomSheet) {
            bottomSheet.classList.remove('active');
        }
        
        if (backdrop) {
            document.body.removeChild(backdrop);
        }
    }

    /**
     * Handle bottom sheet swipe gestures
     */
    handleBottomSheetSwipe(e) {
        let startY = e.touches[0].clientY;
        let currentY = startY;
        
        const handleMove = (moveEvent) => {
            currentY = moveEvent.touches[0].clientY;
            const deltaY = currentY - startY;
            
            if (deltaY > 0) { // Swiping down
                const bottomSheet = document.getElementById('bottom-sheet');
                if (bottomSheet) {
                    bottomSheet.style.transform = `translateY(${Math.min(deltaY, 200)}px)`;
                }
            }
        };
        
        const handleEnd = () => {
            const deltaY = currentY - startY;
            const bottomSheet = document.getElementById('bottom-sheet');
            
            if (bottomSheet) {
                if (deltaY > 100) { // Threshold for closing
                    this.hideBottomSheet();
                } else {
                    bottomSheet.style.transform = 'translateY(0)'; // Snap back
                }
            }
            
            document.removeEventListener('touchmove', handleMove);
            document.removeEventListener('touchend', handleEnd);
        };
        
        document.addEventListener('touchmove', handleMove, { passive: true });
        document.addEventListener('touchend', handleEnd, { passive: true });
    }

    /**
     * Optimize scrolling for mobile
     */
    optimizeScrolling() {
        // Add smooth scrolling class to scrollable elements
        const scrollableElements = document.querySelectorAll(
            '.overflow-y-auto, .overflow-scroll, [data-scroll="smooth"]'
        );
        
        scrollableElements.forEach(element => {
            element.classList.add('smooth-scroll');
        });
        
        // Prevent overscroll on iOS
        if (this.isIOS) {
            document.body.style.overscrollBehavior = 'none';
        }
    }

    /**
     * Handle iOS viewport issues
     */
    handleIOSViewport() {
        if (this.isIOS) {
            // Fix viewport height on iOS
            const setViewportHeight = () => {
                const vh = window.innerHeight * 0.01;
                document.documentElement.style.setProperty('--vh', `${vh}px`);
            };
            
            setViewportHeight();
            window.addEventListener('resize', setViewportHeight);
            window.addEventListener('orientationchange', () => {
                SecureDOM.safeTimeout(setViewportHeight, 100);
            });
            
            // Prevent zoom on input focus
            const meta = document.querySelector('meta[name="viewport"]');
            if (meta) {
                meta.setAttribute('content', 
                    'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
                );
            }
        }
    }

    /**
     * Setup responsive images
     */
    setupResponsiveImages() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('mobile-skeleton');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => {
                img.classList.add('mobile-skeleton');
                imageObserver.observe(img);
            });
        }
    }

    /**
     * Setup progressive loading for content
     */
    setupProgressiveLoading() {
        const loadingElements = document.querySelectorAll('[data-progressive-load]');
        
        if ('IntersectionObserver' in window) {
            const contentObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const element = entry.target;
                        const loadUrl = element.dataset.progressiveLoad;
                        
                        if (loadUrl) {
                            this.loadProgressiveContent(element, loadUrl);
                        }
                        
                        contentObserver.unobserve(element);
                    }
                });
            }, { rootMargin: '100px' });
            
            loadingElements.forEach(element => {
                contentObserver.observe(element);
            });
        }
    }

    /**
     * Load progressive content
     */
    async loadProgressiveContent(element, url) {
        try {
            element.classList.add('mobile-skeleton');
            
            const response = await fetch(url);
            const content = await response.text();
            
            element.innerHTML = content;
            element.classList.remove('mobile-skeleton');
        } catch (error) {
            console.error('Error loading progressive content:', error);
            SecureDOM.setErrorState(element, 'Failed to load content');
        }
    }

    /**
     * Add swipe indicator animation
     */
    addSwipeIndicator() {
        const indicator = SecureDOM.createElement('div', {
            className: 'swipe-indicator swiping',
            style: { 
                position: 'fixed', 
                top: '50%', 
                left: '20px', 
                width: '100px', 
                height: '4px',
                background: '#3b82f6',
                borderRadius: '2px',
                zIndex: '1000'
            }
        });
        
        document.body.appendChild(indicator);
        
        SecureDOM.safeTimeout(() => {
            if (document.body.contains(indicator)) {
                document.body.removeChild(indicator);
            }
        }, 300);
    }

    /**
     * Show card actions on swipe
     */
    showCardActions(card) {
        // Add swipe actions if they don't exist
        let actionsPanel = card.querySelector('.swipe-actions');
        
        if (!actionsPanel) {
            actionsPanel = SecureDOM.createElement('div', {
                className: 'swipe-actions',
                style: {
                    position: 'absolute',
                    right: '0',
                    top: '0',
                    bottom: '0',
                    width: '120px',
                    background: '#ef4444',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    transform: 'translateX(100%)',
                    transition: 'transform 0.3s ease'
                }
            });
            
            const deleteBtn = SecureDOM.createElement('button', {
                className: 'text-white font-semibold'
            }, 'Delete');
            
            actionsPanel.appendChild(deleteBtn);
            card.style.position = 'relative';
            card.appendChild(actionsPanel);
        }
        
        // Show actions
        actionsPanel.style.transform = 'translateX(0)';
        
        // Hide after 3 seconds
        SecureDOM.safeTimeout(() => {
            actionsPanel.style.transform = 'translateX(100%)';
        }, 3000);
    }

    /**
     * Debounce utility
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Create floating action button
     */
    createFAB(icon, action, position = 'bottom-right') {
        const fab = SecureDOM.createElement('button', {
            className: `fab fab-${position}`,
            'aria-label': 'Floating action button'
        }, icon);
        
        fab.addEventListener('click', action);
        document.body.appendChild(fab);
        
        return fab;
    }

    /**
     * Show toast notification
     */
    showToast(message, duration = 3000, type = 'info') {
        const toast = SecureDOM.createElement('div', {
            className: `fixed bottom-20 left-1/2 transform -translate-x-1/2 px-6 py-3 rounded-lg text-white font-medium z-50 ${
                type === 'success' ? 'bg-green-500' :
                type === 'error' ? 'bg-red-500' :
                type === 'warning' ? 'bg-yellow-500' :
                'bg-blue-500'
            }`,
            style: { opacity: '0', transform: 'translate(-50%, 20px)' }
        }, message);
        
        document.body.appendChild(toast);
        
        // Animate in
        SecureDOM.safeTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translate(-50%, 0)';
        }, 10);
        
        // Animate out and remove
        SecureDOM.safeTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translate(-50%, 20px)';
            
            SecureDOM.safeTimeout(() => {
                if (document.body.contains(toast)) {
                    document.body.removeChild(toast);
                }
            }, 300);
        }, duration);
    }
}

// Initialize mobile enhancements
document.addEventListener('DOMContentLoaded', () => {
    window.mobileEnhancements = new MobileEnhancements();
});

// Export for use in other modules
window.MobileEnhancements = MobileEnhancements;