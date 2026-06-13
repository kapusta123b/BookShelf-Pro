(function () {
  var btn = document.getElementById("js-cancel");
  if (!btn) return;

  var ref = document.referrer;
  var isSameOrigin = ref && new URL(ref).origin === location.origin;
  var isDifferentPage = ref && ref !== location.href;

  if (isSameOrigin && isDifferentPage) {
    btn.href = ref;
  } else {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      history.back();
    });
  }
})();
