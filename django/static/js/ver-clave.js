// Botón del ojo en los campos de contraseña: muestra u oculta lo que se escribió.
// El botón empieza oculto: si el navegador no ejecuta JavaScript, el campo funciona igual.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".password-field__toggle").forEach((boton) => {
    const campo = document.getElementById(boton.getAttribute("aria-controls"));
    if (!campo) return;
    const ojo = boton.querySelector(".password-field__eye");
    const ojoTachado = boton.querySelector(".password-field__eye-off");
    boton.hidden = false;

    boton.addEventListener("click", () => {
      const mostrar = campo.type === "password";
      campo.type = mostrar ? "text" : "password";
      boton.setAttribute("aria-pressed", String(mostrar));
      boton.setAttribute("aria-label", mostrar ? "Ocultar contraseña" : "Mostrar contraseña");
      ojo.hidden = mostrar;
      ojoTachado.hidden = !mostrar;
      campo.focus();
    });
  });
});
