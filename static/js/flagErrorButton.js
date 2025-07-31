(function() {
  // ----- Modal for displaying open flags -----
  function createFlagsModal() {
    const modal = document.createElement('div');
    modal.id = 'open-flags-modal';
    modal.className = 'modal modal-hidden fixed inset-0 bg-black bg-opacity-70 z-50 flex justify-center items-center opacity-0';
    modal.innerHTML = `
      <div class="modal-content bg-slate-800 rounded-2xl p-8 max-w-md w-full mx-4 relative scale-95">
        <button id="close-flags-modal" class="absolute top-4 right-4 text-gray-400 hover:text-white">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
        <h2 class="text-2xl font-bold text-white mb-4">Open Flagged Items</h2>
        <div id="open-flags-list" class="space-y-2 max-h-60 overflow-y-auto text-gray-200 mb-4"></div>
        <button id="report-issue-btn" class="bg-yellow-400 text-slate-900 font-bold py-2 px-6 rounded-full hover:bg-yellow-300 w-full">Report Issue</button>
      </div>`;
    document.body.appendChild(modal);
    return modal;
  }

  const flagsModal = createFlagsModal();
  const flagsList = flagsModal.querySelector('#open-flags-list');
  const closeFlagsBtn = flagsModal.querySelector('#close-flags-modal');
  const reportIssueBtn = flagsModal.querySelector('#report-issue-btn');

  function showFlagsModal() {
    flagsModal.classList.remove('modal-hidden');
    setTimeout(() => {
      flagsModal.classList.remove('opacity-0');
      flagsModal.querySelector('.modal-content').classList.remove('scale-95');
    }, 10);
  }

  function hideFlagsModal() {
    flagsModal.classList.add('opacity-0');
    flagsModal.querySelector('.modal-content').classList.add('scale-95');
    setTimeout(() => flagsModal.classList.add('modal-hidden'), 300);
  }

  function openFlagsModal() {
    return new Promise(resolve => {
      flagsList.innerHTML = '<p class="text-center text-gray-400">Loading...</p>';

      function cleanup(value) {
        hideFlagsModal();
        closeFlagsBtn.removeEventListener('click', onClose);
        flagsModal.removeEventListener('click', onBackdrop);
        reportIssueBtn.removeEventListener('click', onReport);
        resolve(value);
      }
      function onClose() { cleanup(false); }
      function onBackdrop(e) { if (e.target === flagsModal) cleanup(false); }
      function onReport() { cleanup(true); }

      closeFlagsBtn.addEventListener('click', onClose);
      flagsModal.addEventListener('click', onBackdrop);
      reportIssueBtn.addEventListener('click', onReport);

      showFlagsModal();

      fetch('/api/open-flags')
        .then(resp => resp.ok ? resp.json() : Promise.reject('Failed to load'))
        .then(flags => {
          if (flags.length === 0) {
            flagsList.innerHTML = '<p class="text-center text-gray-400">No open flagged items.</p>';
          } else {
            const ul = document.createElement('ul');
            ul.className = 'list-disc pl-5 text-left space-y-4';
            flags.forEach(f => {
              const li = document.createElement('li');
              li.innerHTML = `
                <div class="font-semibold">${f.ItemType}: ${f.ItemName || 'ID: ' + f.FlaggedItemID}</div>
                <div class="text-center text-xl text-yellow-300">${f.Reason}</div>
              `;
              ul.appendChild(li);
            });
            flagsList.innerHTML = '';
            flagsList.appendChild(ul);
          }
        })
        .catch(err => {
          console.error('Failed fetching open flags:', err);
          flagsList.innerHTML = '<p class="text-center text-red-400">Error loading flags.</p>';
        });
    });
  }

  // ----- Button for reporting -----
  function createButton() {
    const btn = document.createElement('button');
    btn.id = 'flag-error-btn';
    btn.textContent = 'Flag Error';
    btn.className = 'fixed bottom-4 right-4 bg-red-600 text-white px-4 py-2 rounded-full shadow-lg hover:bg-red-500 z-50';
    btn.addEventListener('click', async function() {
      const proceed = await openFlagsModal();
      if (!proceed) return;

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
    document.body.appendChild(createButton());
  });
})();
