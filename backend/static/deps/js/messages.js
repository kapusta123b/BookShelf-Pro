document.addEventListener("DOMContentLoaded", () => {
  const toasts = document.querySelectorAll(".message-toast");

  toasts.forEach((toast) => {
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(-10px)";
      toast.style.marginTop = `-${toast.offsetHeight}px`;

      setTimeout(() => {
        toast.remove();
        const container = document.getElementById("messages-container");
        if (container && container.children.length === 0) {
          container.remove();
        }
      }, 300);
    }, 5000);
  });
});
