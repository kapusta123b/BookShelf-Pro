document.addEventListener("DOMContentLoaded", function () {
  const mobileToggle = document.querySelector(".nav__mobile-toggle");
  const mobileMenu = document.querySelector(".nav-mobile");

  if (mobileToggle && mobileMenu) {
    mobileToggle.addEventListener("click", function () {
      const isOpen = mobileMenu.classList.toggle("open");
      document.body.style.overflow = isOpen ? "hidden" : "";

      const menuIcon = mobileToggle.querySelector("img");
      if (menuIcon) {
        menuIcon.src = isOpen
          ? menuIcon.src.replace("menu.svg", "close.svg")
          : menuIcon.src.replace("close.svg", "menu.svg");
      }
    });

    document.addEventListener("click", function (e) {
      if (!mobileMenu.contains(e.target) && !mobileToggle.contains(e.target)) {
        mobileMenu.classList.remove("open");
        document.body.style.overflow = "";
      }
    });
  }

  const userMenuTrigger = document.querySelector(".nav__user-menu-trigger");
  const userMenuDropdown = document.querySelector(".nav__user-menu-dropdown");
  const userMenuWrapper = document.querySelector(".nav__user-menu");

  if (userMenuTrigger && userMenuDropdown) {
    userMenuTrigger.addEventListener("click", function (e) {
      e.stopPropagation();
      const isOpen = userMenuDropdown.classList.toggle("open");
      userMenuWrapper.classList.toggle("open", isOpen);
    });

    document.addEventListener("click", function (e) {
      if (!userMenuWrapper.contains(e.target)) {
        userMenuDropdown.classList.remove("open");
        userMenuWrapper.classList.remove("open");
      }
    });
  }

  const searchBtn = document.querySelector(".nav__search-btn");
  const searchOverlay = document.querySelector(".search-overlay");
  const searchOverlayClose = document.querySelector(".search-overlay__close");
  const searchInput = document.querySelector(".search-overlay input");

  if (searchBtn && searchOverlay) {
    function openSearch() {
      searchOverlay.classList.add("open");
      document.body.style.overflow = "hidden";
      setTimeout(function () {
        if (searchInput) searchInput.focus();
      }, 100);
    }

    function closeSearch() {
      searchOverlay.classList.remove("open");
      document.body.style.overflow = "";
    }

    searchBtn.addEventListener("click", openSearch);

    if (searchOverlayClose) {
      searchOverlayClose.addEventListener("click", closeSearch);
    }

    searchOverlay.addEventListener("click", function (e) {
      if (e.target === searchOverlay) closeSearch();
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeSearch();
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        openSearch();
      }
    });
  }

  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll(".nav__link, .nav-mobile__link");

  navLinks.forEach(function (link) {
    const href = link.getAttribute("href");
    if (!href) return;

    if (href === "/" && currentPath === "/") {
      link.classList.add("active");
    } else if (href !== "/" && currentPath.startsWith(href)) {
      link.classList.add("active");
    }
  });
});
