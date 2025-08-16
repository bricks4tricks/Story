document.addEventListener('DOMContentLoaded', function() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    const lazyVideos = document.querySelectorAll('video[data-src]');
    const lazyIframes = document.querySelectorAll('iframe[data-src]');

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                
                if (element.tagName === 'IMG') {
                    element.src = element.dataset.src;
                    element.classList.add('fade-in');
                } else if (element.tagName === 'VIDEO') {
                    element.src = element.dataset.src;
                    element.load();
                } else if (element.tagName === 'IFRAME') {
                    element.src = element.dataset.src;
                }
                
                element.removeAttribute('data-src');
                observer.unobserve(element);
            }
        });
    }, {
        rootMargin: '50px 0px',
        threshold: 0.01
    });

    lazyImages.forEach(img => imageObserver.observe(img));
    lazyVideos.forEach(video => imageObserver.observe(video));
    lazyIframes.forEach(iframe => imageObserver.observe(iframe));

    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    const animationObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    animateElements.forEach(el => animationObserver.observe(el));
});