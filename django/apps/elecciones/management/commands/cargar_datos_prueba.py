"""
Comando para cargar datos de prueba (ficticios) en la base de datos.

Uso:
    python manage.py cargar_datos_prueba

Se puede ejecutar varias veces: actualiza los registros existentes en vez de
duplicarlos. Las fechas de las votaciones se calculan desde el momento en que
se ejecuta, para que siempre haya votaciones abiertas, próximas y cerradas.
"""

from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.elecciones.models import Categoria, Edicion, Opcion, Votacion


def a_las(dias, hora):
    """Fecha y hora local: 'dias' desde hoy (negativo = en el pasado) a la hora indicada."""
    dia = timezone.localdate() + timedelta(days=dias)
    return timezone.make_aware(datetime(dia.year, dia.month, dia.day, hora))


def fecha_fija(anio, mes, dia, hora):
    return timezone.make_aware(datetime(anio, mes, dia, hora))


# Todos los nombres son ficticios, igual que en el prototipo de la Entrega 1.
EDICIONES = [
    {
        'numero': 60, 'anio': 2027, 'nombre': 'Festival de la Leyenda Vallenata',
        'fecha_inicio': date(2027, 4, 28), 'fecha_fin': date(2027, 5, 1),
        'categorias': [
            {
                'nombre': 'Música', 'descripcion': 'Canciones y agrupaciones de la edición.',
                'votaciones': [
                    {
                        'titulo': 'Canción favorita del público',
                        'descripcion': 'Escoge la canción que más te gustó de las presentadas en tarima.',
                        'apertura': lambda: a_las(-2, 8), 'cierre': lambda: a_las(9, 20), 'publicada': True,
                        'opciones': [('Canción A', 'Aire: paseo'), ('Canción B', 'Aire: merengue'),
                                     ('Canción C', 'Aire: son'), ('Canción D', 'Aire: puya')],
                    },
                    {
                        'titulo': 'Agrupación favorita del público',
                        'descripcion': 'Escoge la agrupación que más disfrutaste durante el Festival.',
                        'apertura': lambda: a_las(-1, 8), 'cierre': lambda: a_las(6, 20), 'publicada': True,
                        'opciones': [('Conjunto A', 'Categoría profesional'), ('Conjunto B', 'Categoría aficionado'),
                                     ('Conjunto C', 'Categoría juvenil'), ('Conjunto D', 'Categoría infantil')],
                    },
                    {
                        'titulo': 'Mejor intérprete de acordeón (borrador)',
                        'descripcion': 'Votación en preparación: no debe verse en el sitio público.',
                        'apertura': lambda: a_las(10, 8), 'cierre': lambda: a_las(15, 20), 'publicada': False,
                        'opciones': [('Intérprete A', ''), ('Intérprete B', '')],
                    },
                ],
            },
            {
                'nombre': 'Piloneras y vestuario', 'descripcion': 'Presentaciones de baile y su vestuario.',
                'votaciones': [
                    {
                        'titulo': 'Vestuario más destacado',
                        'descripcion': 'Escoge el vestuario que más te llamó la atención en el Desfile de Piloneras.',
                        'apertura': lambda: a_las(4, 8), 'cierre': lambda: a_las(12, 20), 'publicada': True,
                        'opciones': [('Vestuario A', 'Piloneras mayores'), ('Vestuario B', 'Piloneras juveniles'),
                                     ('Vestuario C', 'Piloneras infantiles')],
                    },
                ],
            },
            {
                'nombre': 'Presentaciones', 'descripcion': 'Momentos destacados de las tarimas.',
                'votaciones': [
                    {
                        'titulo': 'Presentación más recordada',
                        'descripcion': 'Escoge la presentación que más recuerdas de esta edición.',
                        'apertura': lambda: a_las(-12, 8), 'cierre': lambda: a_las(-1, 20), 'publicada': True,
                        'opciones': [('Presentación A', 'Tarima de ejemplo 1'), ('Presentación B', 'Tarima de ejemplo 2'),
                                     ('Presentación C', 'Tarima de ejemplo 3')],
                    },
                ],
            },
        ],
    },
    {
        'numero': 59, 'anio': 2026, 'nombre': 'Festival de la Leyenda Vallenata',
        'fecha_inicio': date(2026, 4, 29), 'fecha_fin': date(2026, 5, 2),
        'categorias': [
            {
                'nombre': 'Música', 'descripcion': 'Canciones de la edición anterior.',
                'votaciones': [
                    {
                        'titulo': 'Canción favorita del público 2026',
                        'descripcion': 'Votación de ejemplo de una edición pasada, ya cerrada.',
                        'apertura': lambda: fecha_fija(2026, 4, 20, 8), 'cierre': lambda: fecha_fija(2026, 5, 2, 20),
                        'publicada': True,
                        'opciones': [('Canción E', 'Aire: paseo'), ('Canción F', 'Aire: son'), ('Canción G', 'Aire: puya')],
                    },
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = 'Carga ediciones, categorías, votaciones y opciones ficticias para probar el sistema.'

    @transaction.atomic  # si algo falla, no queda nada a medias
    def handle(self, *args, **options):
        totales = {'ediciones': 0, 'categorias': 0, 'votaciones': 0, 'opciones': 0}

        for datos_edicion in EDICIONES:
            edicion, _ = Edicion.objects.update_or_create(
                numero=datos_edicion['numero'],
                defaults={
                    'anio': datos_edicion['anio'],
                    'nombre': datos_edicion['nombre'],
                    'fecha_inicio': datos_edicion['fecha_inicio'],
                    'fecha_fin': datos_edicion['fecha_fin'],
                    'activa': True,
                },
            )
            totales['ediciones'] += 1

            for datos_categoria in datos_edicion['categorias']:
                categoria, _ = Categoria.objects.update_or_create(
                    edicion=edicion,
                    nombre=datos_categoria['nombre'],
                    defaults={'descripcion': datos_categoria['descripcion'], 'activa': True},
                )
                totales['categorias'] += 1

                for datos_votacion in datos_categoria['votaciones']:
                    votacion, _ = Votacion.objects.update_or_create(
                        categoria=categoria,
                        titulo=datos_votacion['titulo'],
                        defaults={
                            'descripcion': datos_votacion['descripcion'],
                            'fecha_apertura': datos_votacion['apertura'](),
                            'fecha_cierre': datos_votacion['cierre'](),
                            'publicada': datos_votacion['publicada'],
                        },
                    )
                    totales['votaciones'] += 1

                    for orden, (nombre, descripcion) in enumerate(datos_votacion['opciones'], start=1):
                        Opcion.objects.update_or_create(
                            votacion=votacion,
                            nombre=nombre,
                            defaults={'descripcion': descripcion, 'orden': orden},
                        )
                        totales['opciones'] += 1

        self.stdout.write(self.style.SUCCESS(
            'Datos de prueba cargados: {ediciones} ediciones, {categorias} categorías, '
            '{votaciones} votaciones y {opciones} opciones.'.format(**totales)
        ))
