document.addEventListener("DOMContentLoaded", function () {
  document
    .querySelectorAll(".password-field__toggle")
    .forEach(function (toggle) {
      toggle.addEventListener("click", function () {
        var targetId = toggle.dataset.target;
        var input = targetId
          ? document.getElementById(targetId)
          : toggle.closest(".password-field").querySelector("input");
        if (input) {
          input.type = input.type === "text" ? "password" : "text";
        }
      });
    });
});
