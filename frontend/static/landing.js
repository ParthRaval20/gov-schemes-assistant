document.addEventListener('DOMContentLoaded', () => {
    // Scroll Animation Observer
    const observerOptions = {
        threshold: 0.2, // Trigger when 20% of element is visible
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // Once visible, stop observing this specific element
                // observer.unobserve(entry.target); 
            }
        });
    }, observerOptions);

    // Select all elements with animation classes
    const animElements = document.querySelectorAll('.animate-up, .animate-fade, .animate-reveal');
    animElements.forEach(el => observer.observe(el));

    // Smooth Scroll for Nav Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Offset for fixed nav
                    behavior: 'smooth'
                });
            }
        });
    });

    // Glass Nav effect on scroll
    const nav = document.querySelector('nav');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.style.padding = '10px 0';
            nav.style.backgroundColor = 'rgba(10, 10, 32, 0.9)';
        } else {
            nav.style.padding = '15px 0';
            nav.style.backgroundColor = 'transparent';
        }
    });

    // Add immediate visibility to hero elements if they're in view on load
    const heroAnims = document.querySelectorAll('.hero .animate-up, .hero .animate-fade');
    heroAnims.forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight) {
            el.classList.add('visible');
        }
    });
});
