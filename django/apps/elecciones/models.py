"""
Modelos del dominio del Festival.

Jerarquía: Edicion → Categoria → Votacion → Opcion.
Cada nivel pertenece al anterior mediante una llave foránea (ForeignKey).
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Edicion(models.Model):
    """Una edición anual del Festival (por ejemplo, la 60.ª en 2027)."""

    numero = models.PositiveSmallIntegerField('número', unique=True)
    anio = models.PositiveSmallIntegerField('año', unique=True)
    nombre = models.CharField(max_length=150)
    lugar = models.CharField(max_length=100, default='Valledupar')
    fecha_inicio = models.DateField('fecha de inicio')
    fecha_fin = models.DateField('fecha de fin')
    activa = models.BooleanField(default=True, help_text='Las ediciones inactivas no se muestran en el sitio.')

    class Meta:
        verbose_name = 'edición'
        verbose_name_plural = 'ediciones'
        ordering = ['-anio']

    def __str__(self):
        return f'{self.numero}.ª edición ({self.anio})'

    def clean(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({'fecha_fin': 'La fecha de fin no puede ser anterior a la de inicio.'})


class Categoria(models.Model):
    """Agrupa votaciones dentro de una edición (por ejemplo, "Canción inédita")."""

    # PROTECT: no deja borrar una edición mientras tenga categorías
    edicion = models.ForeignKey(Edicion, on_delete=models.PROTECT, related_name='categorias', verbose_name='edición')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField('descripción', blank=True)
    activa = models.BooleanField(default=True, help_text='Las categorías inactivas no se muestran en el sitio.')

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['edicion', 'nombre']
        constraints = [
            # Una edición no puede tener dos categorías con el mismo nombre
            models.UniqueConstraint(fields=['edicion', 'nombre'], name='categoria_unica_por_edicion'),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.edicion.anio})'


class Votacion(models.Model):
    """Una votación del público dentro de una categoría."""

    # Estados posibles. No se guardan en la base: se calculan con las fechas.
    PROXIMA = 'proxima'
    ABIERTA = 'abierta'
    CERRADA = 'cerrada'

    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='votaciones', verbose_name='categoría')
    titulo = models.CharField('título', max_length=200)
    descripcion = models.TextField('descripción', blank=True)
    fecha_apertura = models.DateTimeField('fecha de apertura')
    fecha_cierre = models.DateTimeField('fecha de cierre')
    publicada = models.BooleanField(default=False, help_text='Mientras no esté publicada, solo se ve en el panel de administración.')

    class Meta:
        verbose_name = 'votación'
        verbose_name_plural = 'votaciones'
        ordering = ['fecha_apertura']

    def __str__(self):
        return self.titulo

    def clean(self):
        if self.fecha_apertura and self.fecha_cierre and self.fecha_cierre <= self.fecha_apertura:
            raise ValidationError({'fecha_cierre': 'La fecha de cierre debe ser posterior a la de apertura.'})

    @property
    def estado(self):
        """Devuelve 'proxima', 'abierta' o 'cerrada' según la hora actual."""
        ahora = timezone.now()
        if ahora < self.fecha_apertura:
            return self.PROXIMA
        if ahora < self.fecha_cierre:
            return self.ABIERTA
        return self.CERRADA

    def get_estado_display(self):
        """Texto del estado para mostrar en pantalla."""
        return {self.PROXIMA: 'Próxima', self.ABIERTA: 'Abierta', self.CERRADA: 'Cerrada'}[self.estado]


class Opcion(models.Model):
    """Una de las alternativas por las que se puede votar."""

    # CASCADE: si se borra la votación, sus opciones se borran con ella
    votacion = models.ForeignKey(Votacion, on_delete=models.CASCADE, related_name='opciones', verbose_name='votación')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField('descripción', blank=True)
    imagen = models.ImageField(upload_to='opciones/', blank=True)
    orden = models.PositiveSmallIntegerField(default=0, help_text='Las opciones se muestran de menor a mayor.')

    class Meta:
        verbose_name = 'opción'
        verbose_name_plural = 'opciones'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre
