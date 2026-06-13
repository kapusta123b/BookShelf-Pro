document.addEventListener("DOMContentLoaded", function () {
  document
    .querySelectorAll(".profile-review__content")
    .forEach(function (content) {
      if (content.scrollHeight > content.clientHeight + 2) {
        const btn = content.nextElementSibling;
        if (!btn || !btn.classList.contains("profile-review__read-more"))
          return;

        btn.hidden = false;

        btn.addEventListener("click", function () {
          const expanded = content.classList.toggle("expanded");
          btn.textContent = expanded ? "Show less" : "Read more";
        });
      }
    });

  document
    .querySelectorAll(".profile-review__spoiler-reveal")
    .forEach(function (btn) {
      btn.addEventListener("click", function () {
        const notice = btn.closest(".profile-review__spoiler-notice");
        const textBlock = notice && notice.nextElementSibling;

        if (
          textBlock &&
          textBlock.classList.contains("profile-review__text--spoiler")
        ) {
          textBlock.classList.add("revealed");
          notice.remove();
        }
      });
    });
});
