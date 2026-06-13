function initReviewReadMore() {
  document
    .querySelectorAll(".book-detail__review-text")
    .forEach(function (text) {
      if (text.dataset.rmInit) return;
      text.dataset.rmInit = "1";

      text.classList.add("expanded");
      const fullHeight = text.offsetHeight;
      text.classList.remove("expanded");
      const clampedHeight = text.offsetHeight;

      if (fullHeight <= clampedHeight + 2) return;

      const btn = text.nextElementSibling;
      if (!btn || !btn.classList.contains("book-detail__review-more")) return;

      btn.hidden = false;
      btn.addEventListener("click", function () {
        const expanded = text.classList.toggle("expanded");
        btn.textContent = expanded ? "Show less" : "Read more";
      });
    });
}

document
  .querySelectorAll(".book-detail__review-spoiler-btn")
  .forEach(function (btn) {
    btn.addEventListener("click", function () {
      const warning = btn.closest(".book-detail__review-spoiler-warning");
      const block = btn.closest(".book-detail__review-spoiler-block");
      const text =
        block && block.querySelector(".book-detail__review-text--blurred");
      if (text) {
        text.classList.add("revealed");
        initReviewReadMore();
      }
      if (warning) warning.remove();
    });
  });

window.addEventListener("load", initReviewReadMore);

document.addEventListener("DOMContentLoaded", function () {
  const widget = document.getElementById("star-vote");
  if (!widget) return;

  const btns = widget.querySelectorAll(".star-vote__btn");
  const input = document.getElementById("vote-input");
  const form = document.getElementById("vote-form");
  const currentVal = parseInt(widget.dataset.current, 10) || 0;

  function highlight(upTo) {
    btns.forEach(function (b) {
      b.classList.toggle("is-active", parseInt(b.dataset.val, 10) <= upTo);
    });
  }

  highlight(currentVal);

  btns.forEach(function (btn) {
    var val = parseInt(btn.dataset.val, 10);

    btn.addEventListener("mouseenter", function () {
      highlight(val);
    });

    btn.addEventListener("click", function () {
      input.value = val;
      form.submit();
    });
  });

  widget.addEventListener("mouseleave", function () {
    highlight(currentVal);
  });
});
