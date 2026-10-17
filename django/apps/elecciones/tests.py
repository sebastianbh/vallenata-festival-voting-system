"""
Pruebas de la app elecciones.

Se ejecutan con:  python manage.py test
Django crea una base de datos temporal para las pruebas y la borra al terminar.
"""

from datetime import date, timedelta
from io import StringIO

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Categoria, Edicion, Opcion, Votacion


def crear_votacion(categoria, titulo, dias_apertura, dias_cierre, publicada=True):
    ahora = timezone.now()
    return Votacion.objects.create(
        categoria=categoria, titulo=titulo, publicada=publicada,
        fecha_apertura=ahora + timedelta(days=dias_apertura),
        fecha_cierre=ahora + timedelta(days=dias_cierre),
    )


class EstadoVotacionTests(TestCase):
    def test_estado_se_calcula_con_las_fechas(self):
        ahora = timezone.now()
        casos = [(1, 5, 'Próxima'), (-1, 5, 'Abierta'), (-5, -1, 'Cerrada')]
        for apertura, cierre, esperado in casos:
            votacion = Votacion(fecha_apertura=ahora + timedelta(days=apertura), fecha_cierre=ahora + timedelta(days=cierre))
            self.assertEqual(votacion.get_estado_display(), esperado)

    def test_cierre_antes_de_apertura_no_es_valido(self):
        ahora = timezone.now()
        votacion = Votacion(titulo='X', fecha_apertura=ahora, fecha_cierre=ahora - timedelta(hours=1))
        with self.assertRaises(ValidationError):
            votacion.clean()


class VistasPublicasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.edicion = Edicion.objects.create(
            numero=60, anio=2027, nombre='Festival de prueba',
            fecha_inicio=date(2027, 4, 28), fecha_fin=date(2027, 5, 1),
        )
        cls.categoria = Categoria.objects.create(edicion=cls.edicion, nombre='Música')
        cls.abierta = crear_votacion(cls.categoria, 'Votación abierta', -1, 5)
        cls.borrador = crear_votacion(cls.categoria, 'Votación borrador', -1, 5, publicada=False)
        Opcion.objects.create(votacion=cls.abierta, nombre='Opción A')

    def test_inicio_muestra_votaciones_abiertas(self):
        respuesta = self.client.get(reverse('elecciones:inicio'))
        self.assertContains(respuesta, 'Votación abierta')
        self.assertNotContains(respuesta, 'Votación borrador')

    def test_paginas_de_navegacion(self):
        urls = [
            reverse('elecciones:lista_ediciones'),
            reverse('elecciones:detalle_edicion', args=[self.edicion.pk]),
            reverse('elecciones:detalle_categoria', args=[self.categoria.pk]),
            reverse('elecciones:detalle_votacion', args=[self.abierta.pk]),
        ]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_detalle_muestra_las_opciones(self):
        respuesta = self.client.get(reverse('elecciones:detalle_votacion', args=[self.abierta.pk]))
        self.assertContains(respuesta, 'Opción A')

    def test_borrador_no_es_publico(self):
        respuesta = self.client.get(reverse('elecciones:detalle_votacion', args=[self.borrador.pk]))
        self.assertEqual(respuesta.status_code, 404)

    def test_categoria_inactiva_no_es_publica(self):
        Categoria.objects.filter(pk=self.categoria.pk).update(activa=False)
        respuesta = self.client.get(reverse('elecciones:detalle_categoria', args=[self.categoria.pk]))
        self.assertEqual(respuesta.status_code, 404)


class DatosPruebaTests(TestCase):
    def test_comando_se_puede_ejecutar_dos_veces_sin_duplicar(self):
        call_command('cargar_datos_prueba', stdout=StringIO())
        call_command('cargar_datos_prueba', stdout=StringIO())
        self.assertEqual(Edicion.objects.count(), 2)
        self.assertEqual(Votacion.objects.count(), 6)
