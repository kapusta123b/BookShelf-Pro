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
