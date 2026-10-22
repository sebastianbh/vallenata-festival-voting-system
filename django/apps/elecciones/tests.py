"""
Pruebas de la app elecciones.

Se ejecutan con:  python manage.py test
Django crea una base de datos temporal para las pruebas y la borra al terminar.
"""

from datetime import date, timedelta
from io import StringIO

from django.contrib.auth.models import User
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


class EdicionPortadaTests(TestCase):
    def crear_edicion(self, numero, anio, **extra):
        return Edicion.objects.create(
            numero=numero, anio=anio, nombre='Festival de prueba',
            fecha_inicio=date(anio, 4, 28), fecha_fin=date(anio, 5, 1), **extra,
        )

    def test_sin_marcar_se_muestra_la_mas_reciente(self):
        self.crear_edicion(59, 2026)
        reciente = self.crear_edicion(60, 2027)
        self.assertEqual(Edicion.de_portada(), reciente)

    def test_se_muestra_la_marcada_aunque_sea_antigua(self):
        antigua = self.crear_edicion(59, 2026, en_portada=True)
        self.crear_edicion(60, 2027)
        self.assertEqual(Edicion.de_portada(), antigua)
        self.assertContains(self.client.get(reverse('elecciones:inicio')), 'hero__edition-number">59<')

    def test_solo_una_edicion_queda_marcada(self):
        primera = self.crear_edicion(59, 2026, en_portada=True)
        segunda = self.crear_edicion(60, 2027, en_portada=True)
        primera.refresh_from_db()
        self.assertFalse(primera.en_portada)
        self.assertTrue(segunda.en_portada)

    def test_una_edicion_inactiva_no_sale_en_portada(self):
        self.crear_edicion(59, 2026, en_portada=True, activa=False)
        reciente = self.crear_edicion(60, 2027)
        self.assertEqual(Edicion.de_portada(), reciente)


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


class AdminTests(TestCase):
    """Comprueba que las pantallas del panel de administración abren sin errores."""

    @classmethod
    def setUpTestData(cls):
        call_command('cargar_datos_prueba', stdout=StringIO())
        cls.admin = User.objects.create_superuser('admin-prueba', 'admin@ejemplo.co', 'Festival-Prueba-2027')

    def test_listas_y_formularios_del_admin(self):
        self.client.force_login(self.admin)
        for modelo in (Edicion, Categoria, Votacion, Opcion):
            nombre = modelo._meta.model_name
            objeto = modelo.objects.first()
            urls = [
                reverse(f'admin:elecciones_{nombre}_changelist'),
                reverse(f'admin:elecciones_{nombre}_add'),
                reverse(f'admin:elecciones_{nombre}_change', args=[objeto.pk]),
            ]
            for url in urls:
                self.assertEqual(self.client.get(url).status_code, 200, url)


class DatosPruebaTests(TestCase):
    def test_comando_se_puede_ejecutar_dos_veces_sin_duplicar(self):
        call_command('cargar_datos_prueba', stdout=StringIO())
        call_command('cargar_datos_prueba', stdout=StringIO())
        self.assertEqual(Edicion.objects.count(), 2)
        self.assertEqual(Votacion.objects.count(), 6)
