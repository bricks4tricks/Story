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
    const darkModeStored = localStorage.getItem('darkMode');
    const fontSizeStored = localStorage.getItem('fontSize');

    if (darkModeStored !== null && fontSizeStored !== null) {
        applyPreferences(darkModeStored === 'true', fontSizeStored);
        return;
    }

    const userId = localStorage.getItem('userId');
    if (!userId) {
        applyPreferences(false, 'medium');
        return;
    }

    fetch(`/api/preferences/${userId}`)
        .then(res => res.json())
        .then(data => {
            const dm = data.darkMode;
            const fs = data.fontSize || 'medium';
            localStorage.setItem('darkMode', dm);
            localStorage.setItem('fontSize', fs);
            applyPreferences(dm, fs);
        })
        .catch(() => {
            applyPreferences(false, 'medium');
        });
});

