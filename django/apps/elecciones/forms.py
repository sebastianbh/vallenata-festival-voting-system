"""Formulario del voto: aquí están las validaciones que hace Django antes de guardar."""

from django import forms
from django.core.exceptions import ValidationError

from .models import Opcion, Votacion, Voto


class VotoForm(forms.Form):
    opcion = forms.ModelChoiceField(
        queryset=Opcion.objects.none(),
        error_messages={
            'required': 'Elige una opción para continuar.',
            'invalid_choice': 'La opción enviada no pertenece a esta votación.',
        },
    )

    def __init__(self, *args, votacion, usuario, **kwargs):
        super().__init__(*args, **kwargs)
        self.votacion = votacion
        self.usuario = usuario
        # Solo se aceptan opciones de esta votación. Como la votación pertenece a una
        # categoría y la categoría a una edición, también quedan validadas esas dos.
        self.fields['opcion'].queryset = votacion.opciones.all()

    def clean(self):
        datos = super().clean()
        if self.votacion.estado != Votacion.ABIERTA:
            raise ValidationError('Esta votación no está abierta: no recibe votos en este momento.')
        if Voto.de_usuario(self.usuario, self.votacion.categoria):
            raise ValidationError('Ya votaste en esta categoría: solo se permite un voto por categoría y edición.')
        return datos
