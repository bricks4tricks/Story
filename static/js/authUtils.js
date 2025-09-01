/**
 * Authentication utilities for handling token validation and cleanup
 */

// Global function to handle stale tokens after deployments
window.handleStaleToken = function() {
    console.log('Stale token detected after deployment - cleaning up');
    
    // Clear all authentication data
    localStorage.removeItem('token');
    sessionStorage.clear();
    
    // Show user-friendly message
    if (window.location.pathname.includes('dashboard') || window.location.pathname.includes('admin')) {
        alert('Your session has expired due to a system update. Please sign in again.');
        window.location.href = '/signin.html';
    } else {
        // For other pages, just show a subtle notification
        console.log('Authentication session cleared due to system update');
    }
};

// Enhanced fetch wrapper that handles authentication automatically
window.authenticatedFetch = function(url, options = {}) {
    const token = localStorage.getItem('token');
    
    // Add authentication headers
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const fetchOptions = {
        ...options,
        headers,
        credentials: 'same-origin'
    };
    
    return fetch(url, fetchOptions)
        .then(response => {
            // Handle stale token automatically
            if (response.status === 401 && token) {
                window.handleStaleToken();
                throw new Error('Authentication expired');
            }
            return response;
        });
};

// Check token validity on page load
document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('token');
    
    // If we have a token, do a quick validation check
    if (token && (window.location.pathname.includes('dashboard') || window.location.pathname.includes('admin'))) {
        fetch('/api/preferences/current', {
            headers: { 'Authorization': `Bearer ${token}` },
            credentials: 'same-origin'
        })
        .then(response => {
            if (response.status === 401) {
                window.handleStaleToken();
            }
        })
        .catch(() => {
            // Network error or other issues - don't auto-logout
        });
    }
});