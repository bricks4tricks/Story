(function() {
  const modal = document.getElementById('flag-modal');
  if (!modal) return;

  const reasonInput = modal.querySelector('#flag-reason');
  const submitBtn = modal.querySelector('#submit-flag-btn');
  const closeBtn = modal.querySelector('#close-flag-modal');

  // Container for open flags list
  const openFlagsDiv = document.createElement('div');
  openFlagsDiv.id = 'open-flags-list';
  openFlagsDiv.className = 'max-h-56 overflow-y-auto text-sm text-gray-200 mb-4';
  reasonInput.parentElement.insertBefore(openFlagsDiv, reasonInput);

  let resolver = null;

  function showModal() {
    modal.classList.remove('modal-hidden');
    setTimeout(() => {
      modal.classList.remove('opacity-0');
      modal.querySelector('.modal-content').classList.remove('scale-95');
    }, 10);
  }

  function hideModal() {
    modal.classList.add('opacity-0');
    modal.querySelector('.modal-content').classList.add('scale-95');
    setTimeout(() => modal.classList.add('modal-hidden'), 300);
  }

  async function loadOpenFlags() {
    openFlagsDiv.innerHTML = '<p class="text-gray-400">Loading open reports...</p>';
    try {
      const res = await fetch('/api/open-flags');
      if (!res.ok) throw new Error('Failed to fetch');
      const flags = await res.json();
      if (flags.length === 0) {
        openFlagsDiv.innerHTML = '<p class="text-gray-400">No open reports.</p>';
        return;
      }
      openFlagsDiv.innerHTML = flags.map(f =>
        `<div class="border-b border-slate-700 py-2">
           <p class="font-semibold">${f.ItemType}: ${f.ItemName || ('ID: ' + f.FlaggedItemID)}</p>
           <p class="text-xs text-gray-400">${f.Reason}</p>
         </div>`
      ).join('');
    } catch (err) {
      openFlagsDiv.innerHTML = '<p class="text-red-400">Error loading open reports.</p>';
    }
  }

  function finish(value) {
    hideModal();
    if (resolver) {
      resolver(value);
      resolver = null;
    }
    reasonInput.value = '';
  }

  window.openFlagModal = function() {
    // Only load existing flags when the feature is enabled.
    // `window.showFlagReporter` is populated in flagErrorButton.js.
    if (window.showFlagReporter) {
      loadOpenFlags();
    }
    showModal();
    return new Promise(resolve => {
      resolver = resolve;
    });
  };

  closeBtn.addEventListener('click', () => finish(null));
  modal.addEventListener('click', e => { if (e.target === modal) finish(null); });
  submitBtn.addEventListener('click', () => finish(reasonInput.value.trim()));
})();
