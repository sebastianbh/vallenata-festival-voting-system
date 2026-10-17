"""
Formularios de registro e inicio de sesión.

Se basan en los formularios estándar de Django (UserCreationForm y
AuthenticationForm); solo se agregan campos y la clase CSS del prototipo.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class EstiloPrototipoMixin:
    """Pone la clase CSS 'input' del prototipo a todos los campos de texto."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            if not isinstance(campo.widget, forms.CheckboxInput):
                campo.widget.attrs['class'] = 'input'


class IngresoForm(EstiloPrototipoMixin, AuthenticationForm):
    """Formulario de inicio de sesión con usuario y contraseña."""


class RegistroForm(EstiloPrototipoMixin, UserCreationForm):
    """Formulario para crear una cuenta de votante."""

    first_name = forms.CharField(label='Nombre completo', max_length=150)
    email = forms.EmailField(label='Correo electrónico')
    acepta_datos = forms.BooleanField(
        label='Acepto el tratamiento de mis datos personales',
        error_messages={'required': 'Debes aceptar el tratamiento de datos para crear la cuenta.'},
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'username', 'email']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return email
