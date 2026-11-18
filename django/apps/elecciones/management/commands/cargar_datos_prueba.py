"""
Comando para cargar datos de prueba (ficticios) en la base de datos.

Uso:
    python manage.py cargar_datos_prueba

Se puede ejecutar varias veces: actualiza los registros existentes en vez de
duplicarlos. Las fechas de las votaciones se calculan desde el momento en que
se ejecuta, para que siempre haya votaciones abiertas, próximas y cerradas.
"""

from datetime import date, datetime, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.elecciones.models import Categoria, Edicion, Opcion, Votacion, Voto


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
                        'resultados': 'en_vivo',  # para mostrar en la sustentación cómo cambia el conteo al votar
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
                        'apertura': lambda: a_las(-1, 8), 'cierre': lambda: a_las(12, 20), 'publicada': True,
                        'resultados': 'ocultos',
                        'opciones': [('Vestuario A', 'Piloneras mayores'), ('Vestuario B', 'Piloneras juveniles'),
                                     ('Vestuario C', 'Piloneras infantiles')],
                    },
                    {
                        'titulo': 'Grupo de piloneras favorito',
                        'descripcion': 'Escoge el grupo de baile que más disfrutaste en el Desfile de Piloneras.',
                        'apertura': lambda: a_las(4, 8), 'cierre': lambda: a_las(12, 20), 'publicada': True,
                        'opciones': [('Grupo A', 'Piloneras mayores'), ('Grupo B', 'Piloneras juveniles'),
                                     ('Grupo C', 'Piloneras infantiles')],
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
                        'votos_demo': {'Presentación A': 3, 'Presentación B': 5, 'Presentación C': 1},
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
                        'votos_demo': {'Canción E': 4, 'Canción F': 4, 'Canción G': 2},  # un empate para mostrarlo
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
        totales = {'ediciones': 0, 'categorias': 0, 'votaciones': 0, 'opciones': 0, 'votos': 0}

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
                            'resultados': datos_votacion.get('resultados', Votacion.RESULTADOS_AL_CIERRE),
                        },
                    )
                    totales['votaciones'] += 1

                    opciones = {}
                    for orden, (nombre, descripcion) in enumerate(datos_votacion['opciones'], start=1):
                        opciones[nombre], _ = Opcion.objects.update_or_create(
                            votacion=votacion,
                            nombre=nombre,
                            defaults={'descripcion': descripcion, 'orden': orden},
                        )
                        totales['opciones'] += 1

                    totales['votos'] += self.cargar_votos_demo(datos_votacion.get('votos_demo', {}), opciones)

        self.stdout.write(self.style.SUCCESS(
            'Datos de prueba cargados: {ediciones} ediciones, {categorias} categorías, '
            '{votaciones} votaciones, {opciones} opciones y {votos} votos de ejemplo.'.format(**totales)
        ))

    def cargar_votos_demo(self, votos_por_opcion, opciones):
        """
        Votos de ejemplo en votaciones ya cerradas, para que la página de resultados tenga datos.
        Los emiten cuentas ficticias (votante-demo-1, 2, ...) SIN contraseña utilizable: nadie puede
        iniciar sesión con ellas. get_or_create evita duplicar votos si el comando se corre otra vez.
        """
        numero = 0
        for nombre_opcion, cantidad in votos_por_opcion.items():
            opcion = opciones[nombre_opcion]
            categoria = opcion.votacion.categoria
            for _ in range(cantidad):
                numero += 1
                usuario, creado = User.objects.get_or_create(
                    username=f'votante-demo-{numero}', defaults={'first_name': f'Votante de ejemplo {numero}'},
                )
                if creado:
                    usuario.set_unusable_password()
                    usuario.save()
                Voto.objects.get_or_create(
                    usuario=usuario, edicion=categoria.edicion, categoria=categoria, defaults={'opcion': opcion},
                )
        return numero
