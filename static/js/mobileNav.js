document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    const body = document.body;

    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            mobileMenu.classList.toggle('slide-down');
            
            const icon = mobileMenuToggle.querySelector('svg');
            if (mobileMenu.classList.contains('hidden')) {
                const hamburgerPath = SecureDOM.createElement('path', {
                    'stroke-linecap': 'round',
                    'stroke-linejoin': 'round',
                    'stroke-width': '2',
                    'd': 'M4 6h16M4 12h16M4 18h16'
                });
                SecureDOM.replaceContent(icon, hamburgerPath);
            } else {
                const closePath = SecureDOM.createElement('path', {
                    'stroke-linecap': 'round',
                    'stroke-linejoin': 'round',
                    'stroke-width': '2',
                    'd': 'M6 18L18 6M6 6l12 12'
                });
                SecureDOM.replaceContent(icon, closePath);
            }
        });

        document.addEventListener('click', function(event) {
            if (!mobileMenuToggle.contains(event.target) && !mobileMenu.contains(event.target)) {
                mobileMenu.classList.add('hidden');
                const icon = mobileMenuToggle.querySelector('svg');
                const hamburgerPath = SecureDOM.createElement('path', {
                    'stroke-linecap': 'round',
                    'stroke-linejoin': 'round',
                    'stroke-width': '2',
                    'd': 'M4 6h16M4 12h16M4 18h16'
                });
                SecureDOM.replaceContent(icon, hamburgerPath);
            }
        });

        const menuLinks = mobileMenu.querySelectorAll('a');
        menuLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
                const icon = mobileMenuToggle.querySelector('svg');
                const hamburgerPath = SecureDOM.createElement('path', {
                    'stroke-linecap': 'round',
                    'stroke-linejoin': 'round',
                    'stroke-width': '2',
                    'd': 'M4 6h16M4 12h16M4 18h16'
                });
                SecureDOM.replaceContent(icon, hamburgerPath);
            });
        });
    }
});