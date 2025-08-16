/**
 * Secure DOM manipulation utilities to prevent XSS attacks
 * Provides safe alternatives to innerHTML and other potentially dangerous DOM operations
 */

class SecureDOM {
    /**
     * Safely set text content (prevents XSS)
     */
    static setText(element, text) {
        if (!element) return;
        element.textContent = text || '';
    }

    /**
     * Safely create and append HTML elements
     */
    static createElement(tagName, attributes = {}, textContent = '') {
        const element = document.createElement(tagName);
        
        // Set attributes safely
        for (const [key, value] of Object.entries(attributes)) {
            if (key === 'style') {
                // Handle style object
                if (typeof value === 'object') {
                    Object.assign(element.style, value);
                } else {
                    element.style.cssText = value;
                }
            } else if (key.startsWith('data-')) {
                element.setAttribute(key, value);
            } else if (key === 'className') {
                element.className = value;
            } else if (key === 'id') {
                element.id = value;
            } else {
                // Be cautious with other attributes
                element.setAttribute(key, value);
            }
        }
        
        if (textContent) {
            element.textContent = textContent;
        }
        
        return element;
    }

    /**
     * Safely clear container and add new content
     */
    static replaceContent(container, ...elements) {
        if (!container) return;
        
        // Clear existing content
        container.innerHTML = '';
        
        // Add new elements
        elements.forEach(element => {
            if (element instanceof Element) {
                container.appendChild(element);
            } else if (typeof element === 'string') {
                container.appendChild(document.createTextNode(element));
            }
        });
    }

    /**
     * Safely append content to container
     */
    static appendContent(container, ...elements) {
        if (!container) return;
        
        elements.forEach(element => {
            if (element instanceof Element) {
                container.appendChild(element);
            } else if (typeof element === 'string') {
                container.appendChild(document.createTextNode(element));
            }
        });
    }

    /**
     * Sanitize HTML string (basic implementation)
     */
    static sanitizeHTML(html) {
        const temp = document.createElement('div');
        temp.textContent = html;
        return temp.innerHTML;
    }

    /**
     * Create a safe HTML template
     */
    static createTemplate(templateString, data = {}) {
        // Simple template substitution with escaping
        let result = templateString;
        
        for (const [key, value] of Object.entries(data)) {
            const placeholder = new RegExp(`{{\\s*${key}\\s*}}`, 'g');
            const escapedValue = this.sanitizeHTML(String(value));
            result = result.replace(placeholder, escapedValue);
        }
        
        return result;
    }

    /**
     * Safely set loading state
     */
    static setLoadingState(container, message = 'Loading...') {
        if (!container) return;
        
        const loadingDiv = this.createElement('div', {
            className: 'text-center text-gray-400'
        }, message);
        
        this.replaceContent(container, loadingDiv);
    }

    /**
     * Safely set error state
     */
    static setErrorState(container, message = 'An error occurred') {
        if (!container) return;
        
        const errorDiv = this.createElement('div', {
            className: 'text-center text-red-400'
        }, message);
        
        this.replaceContent(container, errorDiv);
    }

    /**
     * Safely set empty state
     */
    static setEmptyState(container, message = 'No data found') {
        if (!container) return;
        
        const emptyDiv = this.createElement('div', {
            className: 'text-center text-gray-400'
        }, message);
        
        this.replaceContent(container, emptyDiv);
    }

    /**
     * Validate and limit setTimeout/setInterval delays
     */
    static safeTimeout(callback, delay = 0, maxDelay = 30000) {
        const safeDelay = Math.min(Math.max(delay, 0), maxDelay);
        return setTimeout(callback, safeDelay);
    }

    static safeInterval(callback, delay = 1000, maxDelay = 30000) {
        const safeDelay = Math.min(Math.max(delay, 100), maxDelay);
        return setInterval(callback, safeDelay);
    }
}

// Make SecureDOM available globally
window.SecureDOM = SecureDOM;

// Provide migration helpers for existing code
window.safeSetText = SecureDOM.setText;
window.safeCreateElement = SecureDOM.createElement;
window.safeReplaceContent = SecureDOM.replaceContent;
window.safeTimeout = SecureDOM.safeTimeout;