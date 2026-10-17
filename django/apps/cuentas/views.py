"""Vistas de registro, inicio y cierre de sesión."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render

from .forms import IngresoForm, RegistroForm


class IngresoView(SuccessMessageMixin, LoginView):
    """Inicio de sesión estándar de Django con la plantilla del prototipo."""

    template_name = 'cuentas/ingresar.html'
    authentication_form = IngresoForm
    redirect_authenticated_user = True
    success_message = 'Hola, %(username)s. Iniciaste sesión.'


class SalidaView(LogoutView):
    """Cierre de sesión. Por seguridad solo se acepta con un formulario (POST)."""

    def post(self, request, *args, **kwargs):
        respuesta = super().post(request, *args, **kwargs)
        messages.info(request, 'Cerraste sesión.')
        return respuesta


def registro(request):
    """Crea la cuenta, inicia la sesión y lleva al inicio."""
    if request.user.is_authenticated:
        return redirect('elecciones:inicio')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f'Bienvenido, {usuario.first_name}. Tu cuenta quedó creada.')
            return redirect('elecciones:inicio')
    else:
        form = RegistroForm()

    return render(request, 'cuentas/registro.html', {'form': form})
