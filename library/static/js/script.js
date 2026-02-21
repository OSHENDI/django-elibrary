// stagger entrance for cards using IntersectionObserver
document.addEventListener('DOMContentLoaded', function () {
    var cards = document.querySelectorAll(
        '.book-card, .category-card, .author-card, .review-card, .borrow-card, .stat-card'
    );
    if (!cards.length) return;

    var observer = new IntersectionObserver(function (entries) {
        var delay = 0;
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                var el = entry.target;
                setTimeout(function () {
                    el.classList.add('visible');
                }, delay);
                delay += 40;
                observer.unobserve(el);
            }
        });
    }, { threshold: 0.08 });

    cards.forEach(function (card) { observer.observe(card); });
});

// star rating picker for review form
document.addEventListener('DOMContentLoaded', function () {
    var picker = document.getElementById('starPicker');
    if (!picker) return;

    var stars = picker.querySelectorAll('i');
    var input = picker.parentElement.querySelector('input[type="hidden"]');

    stars.forEach(function (star) {
        star.addEventListener('mouseenter', function () {
            var val = parseInt(this.dataset.value);
            stars.forEach(function (s) {
                var sv = parseInt(s.dataset.value);
                s.className = sv <= val ? 'fas fa-star active' : 'far fa-star';
            });
        });

        star.addEventListener('click', function () {
            var val = this.dataset.value;
            if (input) input.value = val;
            stars.forEach(function (s) {
                var sv = parseInt(s.dataset.value);
                s.className = sv <= parseInt(val) ? 'fas fa-star active' : 'far fa-star';
            });
        });
    });

    picker.addEventListener('mouseleave', function () {
        var current = input ? parseInt(input.value) : 0;
        stars.forEach(function (s) {
            var sv = parseInt(s.dataset.value);
            s.className = sv <= current ? 'fas fa-star active' : 'far fa-star';
        });
    });
});

// highlight active nav link
document.addEventListener('DOMContentLoaded', function () {
    var path = window.location.pathname;
    var links = document.querySelectorAll('.navbar .nav-link');
    links.forEach(function (link) {
        var href = link.getAttribute('href');
        if (href === path || (href !== '/' && path.startsWith(href))) {
            link.classList.add('active');
        }
    });
});

// auto-dismiss alerts after 4 seconds
document.addEventListener('DOMContentLoaded', function () {
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 4000);
    });
});

// smooth scroll to top on pagination clicks
document.addEventListener('DOMContentLoaded', function () {
    var links = document.querySelectorAll('.pagination .page-link');
    links.forEach(function (link) {
        link.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });
});
