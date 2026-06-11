document.addEventListener('DOMContentLoaded', function () {

  const gridViewBtn = document.querySelector('[data-view="grid"]');
  const listViewBtn = document.querySelector('[data-view="list"]');
  const libraryGrid = document.querySelector('.library-grid');

  if (gridViewBtn && listViewBtn && libraryGrid) {
    function setView(view) {
      if (view === 'list') {
        libraryGrid.classList.add('list-view');
        listViewBtn.classList.add('active');
        gridViewBtn.classList.remove('active');
      } else {
        libraryGrid.classList.remove('list-view');
        gridViewBtn.classList.add('active');
        listViewBtn.classList.remove('active');
      }
      localStorage.setItem('library-view', view);
    }

    const savedView = localStorage.getItem('library-view') || 'grid';
    setView(savedView);

    gridViewBtn.addEventListener('click', function () { setView('grid'); });
    listViewBtn.addEventListener('click', function () { setView('list'); });
  }


  function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeModal(modal) {
    modal.classList.remove('open');
    document.body.style.overflow = '';
  }

  document.querySelectorAll('[data-open-modal]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      openModal(btn.dataset.openModal);
    });
  });

  document.querySelectorAll('.book-modal').forEach(function (modal) {
    modal.querySelectorAll('[data-close-modal]').forEach(function (el) {
      el.addEventListener('click', function () {
        closeModal(modal);
      });
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.book-modal.open').forEach(function (modal) {
        closeModal(modal);
      });
    }
  });

  document.querySelectorAll('.book-modal__status-option input[type="radio"]').forEach(function (radio) {
    radio.addEventListener('change', function () {
      const options = radio.closest('.book-modal__status-options').querySelectorAll('.book-modal__status-option');
      options.forEach(function (opt) { opt.classList.remove('is-active'); });
      radio.closest('.book-modal__status-option').classList.add('is-active');
    });
  });

});
