document.addEventListener('DOMContentLoaded', function () {

  const heroBooks = document.querySelectorAll('.hero__book');
  heroBooks.forEach(function (book, i) {
    book.style.transitionDelay = (i * 0.08) + 's';
    book.style.opacity = '0';
    book.style.transform = book.style.transform + ' translateY(20px)';

    setTimeout(function () {
      book.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      book.style.opacity = '1';
      book.style.transform = book.style.transform.replace(' translateY(20px)', '');
    }, 200 + i * 80);
  });

  const heroSearchInput = document.querySelector('.hero__search-bar input[name="q"]');
  const heroSearchTypeInput = document.querySelector('.hero__search-bar input[name="type"]');
  const heroSearchTabs = document.querySelectorAll('.hero__search-tab');

  heroSearchTabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      heroSearchTabs.forEach(function (t) { t.classList.remove('is-active'); });
      tab.classList.add('is-active');
      if (heroSearchInput) {
        heroSearchInput.placeholder = tab.dataset.placeholder;
        heroSearchInput.focus();
      }
      if (heroSearchTypeInput) {
        heroSearchTypeInput.value = tab.dataset.type;
      }
    });
  });

  const catCards = document.querySelectorAll('.categories__card');
  catCards.forEach(function (card) {
    card.addEventListener('mouseenter', function () {
      const emoji = card.querySelector('.categories__card-emoji');
      if (emoji) {
        emoji.style.transform = 'scale(1.2) rotate(-5deg)';
        setTimeout(function () {
          emoji.style.transform = '';
        }, 200);
      }
    });
  });

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.how-it-works__step, .stats-strip__item').forEach(function (el) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });
});
