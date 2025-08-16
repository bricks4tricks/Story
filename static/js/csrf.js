/**
 * CSRF Token Management Utility
 * Handles CSRF token retrieval and inclusion in API requests
 */

class CSRFManager {
    constructor() {
        this.token = null;
        this.init();
    }

    async init() {
        await this.refreshToken();
    }

    async refreshToken() {
        try {
            const response = await fetch('/api/csrf-token', {
                method: 'GET',
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.token = data.csrf_token;
            } else {
                console.warn('Failed to fetch CSRF token');
            }
        } catch (error) {
            console.error('Error fetching CSRF token:', error);
        }
    }

    getToken() {
        return this.token;
    }

    getHeaders() {
        return this.token ? { 'X-CSRF-Token': this.token } : {};
    }

    async secureRequest(url, options = {}) {
        // Ensure we have a token
        if (!this.token) {
            await this.refreshToken();
        }

        // Add CSRF token to headers
        const headers = {
            'Content-Type': 'application/json',
            ...this.getHeaders(),
            ...(options.headers || {})
        };

        const requestOptions = {
            ...options,
            headers,
            credentials: 'same-origin'
        };

        try {
            const response = await fetch(url, requestOptions);
            
            // If we get a 403, try refreshing the token once
            if (response.status === 403 && !options._retried) {
                await this.refreshToken();
                return this.secureRequest(url, { ...options, _retried: true });
            }
            
            return response;
        } catch (error) {
            console.error('Secure request failed:', error);
            throw error;
        }
    }

    // Convenience methods for common HTTP verbs
    async get(url, options = {}) {
        return this.secureRequest(url, { ...options, method: 'GET' });
    }

    async post(url, data = null, options = {}) {
        return this.secureRequest(url, {
            ...options,
            method: 'POST',
            body: data ? JSON.stringify(data) : undefined
        });
    }

    async put(url, data = null, options = {}) {
        return this.secureRequest(url, {
            ...options,
            method: 'PUT',
            body: data ? JSON.stringify(data) : undefined
        });
    }

    async delete(url, options = {}) {
        return this.secureRequest(url, { ...options, method: 'DELETE' });
    }
}

// Create global instance
window.csrfManager = new CSRFManager();

// Convenience function for secure fetch
window.secureFetch = (url, options = {}) => {
    return window.csrfManager.secureRequest(url, options);
};