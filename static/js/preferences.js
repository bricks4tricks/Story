// Ensure the page starts in light mode when no preference is stored.
// Because this script is injected just before </body>, the body element
// is available immediately. Apply a light theme upfront to avoid a flash
// of dark content for first-time visitors.
const darkModeStored = sessionStorage.getItem('darkMode');
if (darkModeStored === null || darkModeStored === 'false') {
    document.body.classList.add('light');
}

const applyPreferences = (darkMode, fontSize) => {
    if (darkMode) {
        document.body.classList.remove('light');
    } else {
        document.body.classList.add('light');
    }
    const size = fontSize;
    document.body.style.fontSize =
        size === 'small' ? '14px' : size === 'large' ? '18px' : '16px';
};

document.addEventListener('DOMContentLoaded', () => {
    const fontSizeStored = sessionStorage.getItem('fontSize');

    if (darkModeStored !== null && fontSizeStored !== null) {
        applyPreferences(darkModeStored === 'true', fontSizeStored);
        return;
    }

    // For logged-in users, fetch preferences from server
    // Include Authorization header if token is available
    const token = localStorage.getItem('token');
    const headers = {};
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    fetch('/api/preferences/current', {
        headers: headers,
        credentials: 'same-origin'  // Include session cookies too
    })
        .then(res => {
            if (!res.ok) throw new Error('Not logged in');
            return res.json();
        })
        .then(data => {
            const dm = data.darkMode;
            const fs = data.fontSize || 'medium';
            sessionStorage.setItem('darkMode', dm);
            sessionStorage.setItem('fontSize', fs);
            applyPreferences(dm, fs);
        })
        .catch(() => {
            applyPreferences(false, 'medium');
        });
});

