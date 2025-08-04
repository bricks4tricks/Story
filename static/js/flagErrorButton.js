(function() {
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
  document.addEventListener('DOMContentLoaded', function() {
    const loginPages = [
      '/signin.html',
      '/student-login.html',
      '/parent-login.html',
      '/admin-login.html'
    ];
    if (!loginPages.includes(window.location.pathname)) {
      document.body.appendChild(createButton());
    }
  });
})();
