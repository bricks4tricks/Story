(function() {
  const modal = document.getElementById('flag-modal');
  if (!modal) return;

  const reasonInput = modal.querySelector('#flag-reason');
  const submitBtn = modal.querySelector('#submit-flag-btn');
  const closeBtn = modal.querySelector('#close-flag-modal');

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

  function finish(value) {
    hideModal();
    if (resolver) {
      resolver(value);
      resolver = null;
    }
    reasonInput.value = '';
  }

  window.openFlagModal = function() {
    showModal();
    return new Promise(resolve => {
      resolver = resolve;
    });
  };

  closeBtn.addEventListener('click', () => finish(null));
  modal.addEventListener('click', e => { if (e.target === modal) finish(null); });
  submitBtn.addEventListener('click', () => finish(reasonInput.value.trim()));
})();
