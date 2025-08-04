// backToTop.js: controls the visibility and behavior of the Back to Top button.
const btn = document.getElementById('backToTop');
// Show the button when the user scrolls down 300px
window.addEventListener('scroll', () => {
  if (window.scrollY > 300) {
    btn.classList.remove('hidden');
  } else {
    btn.classList.add('hidden');
  }
});
// Smooth scroll to top on click
btn.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});
