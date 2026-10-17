// Abre y cierra el menú principal en pantallas pequeñas (botón de tres rayas).
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");
  if (!toggle || !nav) return;

  const setOpen = (isOpen) => {
    nav.dataset.open = String(isOpen);
    toggle.setAttribute("aria-expanded", String(isOpen));
  };

  toggle.addEventListener("click", () => setOpen(nav.dataset.open !== "true"));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && nav.dataset.open === "true") {
      setOpen(false);
      toggle.focus();
    }
  });
});
