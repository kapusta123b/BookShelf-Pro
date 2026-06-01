document.addEventListener('DOMContentLoaded', function () {

  const gridViewBtn = document.querySelector('[data-view="grid"]');
  const listViewBtn = document.querySelector('[data-view="list"]');
  const booksGrid = document.querySelector('.books-grid-catalog');

  if (gridViewBtn && listViewBtn && booksGrid) {
    function setView(view) {
      if (view === 'list') {
        booksGrid.classList.add('list-view');
        listViewBtn.classList.add('active');
        gridViewBtn.classList.remove('active');
      } else {
        booksGrid.classList.remove('list-view');
        gridViewBtn.classList.add('active');
        listViewBtn.classList.remove('active');
      }
      localStorage.setItem('catalog-view', view);
    }

    const savedView = localStorage.getItem('catalog-view') || 'grid';
    setView(savedView);

    gridViewBtn.addEventListener('click', function () { setView('grid'); });
    listViewBtn.addEventListener('click', function () { setView('list'); });
  }

  const filterToggleBtn = document.querySelector('.catalog__filter-toggle');
  const filtersPanel = document.querySelector('.filters');
  const filtersOverlay = document.querySelector('.filters-overlay');
  const filtersCloseBtn = document.querySelector('.filters__close');

  function openFilters() {
    if (filtersPanel) filtersPanel.classList.add('mobile-open');
    if (filtersOverlay) filtersOverlay.classList.add('mobile-open');
    document.body.style.overflow = 'hidden';
  }

  function closeFilters() {
    if (filtersPanel) filtersPanel.classList.remove('mobile-open');
    if (filtersOverlay) filtersOverlay.classList.remove('mobile-open');
    document.body.style.overflow = '';
  }

  if (filterToggleBtn) filterToggleBtn.addEventListener('click', openFilters);
  if (filtersCloseBtn) filtersCloseBtn.addEventListener('click', closeFilters);
  if (filtersOverlay) filtersOverlay.addEventListener('click', closeFilters);

  const filterGroupHeaders = document.querySelectorAll('.filters__group-header');

  filterGroupHeaders.forEach(function (header, index) {
    const storageKey = 'filter-group-' + index;
    const saved = localStorage.getItem(storageKey);

    if (saved === 'collapsed') {
      header.classList.add('collapsed');
      const body = header.nextElementSibling;
      if (body) body.classList.add('collapsed');
    }

    header.addEventListener('click', function () {
      const body = header.nextElementSibling;
      const isCollapsed = header.classList.toggle('collapsed');
      if (body) body.classList.toggle('collapsed', isCollapsed);
      localStorage.setItem(storageKey, isCollapsed ? 'collapsed' : 'open');
    });
  });

  const catalogSearchInput = document.querySelector('.catalog__search input[name="q"]');
  const catalogSearchTypeInput = document.querySelector('.catalog__search input[name="type"]');
  const catalogSearchTypes = document.querySelectorAll('.catalog__search-type');

  catalogSearchTypes.forEach(function (btn) {
    btn.addEventListener('click', function () {
      catalogSearchTypes.forEach(function (b) { b.classList.remove('is-active'); });
      btn.classList.add('is-active');
      if (catalogSearchInput) {
        catalogSearchInput.placeholder = btn.dataset.placeholder;
        catalogSearchInput.focus();
      }
      if (catalogSearchTypeInput) {
        catalogSearchTypeInput.value = btn.dataset.type;
      }
    });
  });

  const filterCheckboxes = document.querySelectorAll('.filters input[type="checkbox"], .filters input[type="radio"]');
  let activeFiltersCount = 0;

  filterCheckboxes.forEach(function (checkbox) {
    checkbox.addEventListener('change', function () {
      activeFiltersCount = document.querySelectorAll('.filters input[type="checkbox"]:checked, .filters input[type="radio"]:not([value="all"]):checked').length;

      if (filterToggleBtn) {
        filterToggleBtn.classList.toggle('has-filters', activeFiltersCount > 0);
        const countBadge = filterToggleBtn.querySelector('.filter-count');
        if (countBadge) {
          countBadge.textContent = activeFiltersCount > 0 ? activeFiltersCount : '';
          countBadge.style.display = activeFiltersCount > 0 ? 'inline' : 'none';
        }
      }
    });
  });

  const clearBtn = document.querySelector('.filters__clear');
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      filterCheckboxes.forEach(function (input) {
        if (input.type === 'checkbox') input.checked = false;
        if (input.type === 'radio' && input.value === 'all') input.checked = true;
        else if (input.type === 'radio') input.checked = false;
      });

      const yearInputs = document.querySelectorAll('.filters__year input');
      yearInputs.forEach(function (input) { input.value = ''; });

      activeFiltersCount = 0;
      if (filterToggleBtn) filterToggleBtn.classList.remove('has-filters');
    });
  }

  const savedScroll = sessionStorage.getItem('catalog-scroll');
  if (savedScroll) {
    window.scrollTo(0, parseInt(savedScroll, 10));
    sessionStorage.removeItem('catalog-scroll');
  }

  window.addEventListener('pagehide', function () {
    sessionStorage.setItem('catalog-scroll', window.scrollY);
  });

});
