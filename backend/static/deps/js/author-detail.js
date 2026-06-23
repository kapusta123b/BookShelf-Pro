document.addEventListener("DOMContentLoaded", function () {
  var showMoreBtn = document.querySelector('[data-show-more="names"]');
  if (showMoreBtn) {
    var extras = document.querySelectorAll(
      ".author-detail__alternate-name--extra",
    );
    var count = parseInt(showMoreBtn.dataset.count, 10);
    var expanded = false;

    showMoreBtn.addEventListener("click", function () {
      expanded = !expanded;
      extras.forEach(function (el) {
        el.classList.toggle("is-visible", expanded);
      });
      showMoreBtn.textContent = expanded
        ? "Show less"
        : "Show " + count + " more";
    });
  }
});
