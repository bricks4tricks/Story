(function() {
  /**
   * Determine if the "Flag Error" reporter should be shown.
   *
   * Admins can toggle this feature globally by setting
   * `window.showFlagReporter` or via the `/api/config` endpoint.
   */
  async function reporterEnabled() {
    if (typeof window.showFlagReporter !== 'undefined') {
      return !!window.showFlagReporter;
    }
    try {
      const res = await fetch('/api/config');
      if (!res.ok) return false;
      const cfg = await res.json();
      const enabled = !!cfg.showFlagReporter;
      // Persist so other scripts (e.g., flagModal.js) can use the value.
      window.showFlagReporter = enabled;
      return enabled;
    } catch (err) {
      // Treat failures as disabled to avoid showing the button unexpectedly.
      return false;
    }
  }

  function createButton() {
    const btn = document.createElement('button');
    btn.id = 'flag-error-btn';
    btn.textContent = 'Flag Error';
    btn.className = 'fixed bottom-4 right-4 bg-red-600 text-white px-4 py-2 rounded-full shadow-lg hover:bg-red-500 z-50';
    btn.addEventListener('click', async function() {
      let description = '';
      if (typeof openFlagModal === 'function') {
        description = await openFlagModal();
        if (description === null) return;
      } else {
        description = prompt('Describe the issue (optional):') || '';
      }
      fetch('/api/flag-page-error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: parseInt(localStorage.getItem('userId')) || null,
          pagePath: window.location.pathname,
          description: description.trim()
        })
      })
        .then(res => res.json())
        .then(data => {
          alert(data.message || (data.status === 'success'
            ? 'Thank you! Your report has been submitted.'
            : 'Error submitting report.'));
        })
        .catch(() => {
          alert('Could not submit flag. Please try again later.');
        });
    });
    return btn;
  }

  document.addEventListener('DOMContentLoaded', async function() {
    const loginPages = [
      '/signin.h',
      '/student-login.html',
      '/parent-login.html',
      '/admin-login.html'
    ];
    if (loginPages.includes(window.location.pathname)) return;

    // Only append the button when configuration explicitly enables it.
    if (await reporterEnabled()) {
      document.body.appendChild(createButton());
    }
  });
})();
