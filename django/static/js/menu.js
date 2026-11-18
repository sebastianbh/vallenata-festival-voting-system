// Abre y cierra el menú principal en pantallas pequeñas (botón de tres rayas).
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");
  if (!toggle || !nav) return;

  const isOpen = () => nav.dataset.open === "true";
  const setOpen = (open) => {
    nav.dataset.open = String(open);
    toggle.setAttribute("aria-expanded", String(open));
  };

  toggle.addEventListener("click", () => setOpen(!isOpen()));

  // Escape cierra el menú y devuelve el foco al botón
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && isOpen()) {
      setOpen(false);
      toggle.focus();
    }
  });

  // En celular: tocar fuera del menú lo cierra
  document.addEventListener("click", (event) => {
    if (isOpen() && !nav.contains(event.target) && !toggle.contains(event.target)) setOpen(false);
  });

  // Al elegir un enlace, el menú se cierra (útil si el navegador vuelve atrás con la página guardada)
  nav.addEventListener("click", (event) => {
    if (event.target.closest("a")) setOpen(false);
  });

  // Si se gira el celular o se agranda la ventana hasta el menú de escritorio, se reinicia
  window.matchMedia("(min-width: 60rem)").addEventListener("change", () => setOpen(false));
});
