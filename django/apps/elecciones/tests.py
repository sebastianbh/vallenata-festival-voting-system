"""
Pruebas de la app elecciones.

Se ejecutan con:  python manage.py test
Django crea una base de datos temporal para las pruebas y la borra al terminar.
"""

import json
import threading
from datetime import date, timedelta
from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, connection, transaction
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from .models import Categoria, Edicion, Opcion, Votacion, Voto


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
        self.assertEqual(Votacion.objects.count(), 7)


def crear_escenario_de_voto(prueba):
    """Dos subeventos abiertos en Música, uno abierto en Baile, uno cerrado y uno próximo en Historia."""
    prueba.edicion = Edicion.objects.create(
        numero=60, anio=2027, nombre='Festival de prueba',
        fecha_inicio=date(2027, 4, 28), fecha_fin=date(2027, 5, 1),
    )
    prueba.musica = Categoria.objects.create(edicion=prueba.edicion, nombre='Música')
    prueba.baile = Categoria.objects.create(edicion=prueba.edicion, nombre='Baile')
    prueba.historia = Categoria.objects.create(edicion=prueba.edicion, nombre='Historia')

    prueba.cancion = crear_votacion(prueba.musica, 'Canción favorita', -1, 5)
    prueba.conjunto = crear_votacion(prueba.musica, 'Conjunto favorito', -1, 5)
    prueba.vestuario = crear_votacion(prueba.baile, 'Vestuario favorito', -1, 5)
    prueba.cerrada = crear_votacion(prueba.historia, 'Votación cerrada', -5, -1)
    prueba.proxima = crear_votacion(prueba.historia, 'Votación próxima', 1, 5)

    prueba.cancion_a = Opcion.objects.create(votacion=prueba.cancion, nombre='Canción A')
    prueba.cancion_b = Opcion.objects.create(votacion=prueba.cancion, nombre='Canción B')
    prueba.conjunto_a = Opcion.objects.create(votacion=prueba.conjunto, nombre='Conjunto A')
    prueba.vestuario_a = Opcion.objects.create(votacion=prueba.vestuario, nombre='Vestuario A')
    prueba.cerrada_a = Opcion.objects.create(votacion=prueba.cerrada, nombre='Cerrada A')
    prueba.proxima_a = Opcion.objects.create(votacion=prueba.proxima, nombre='Próxima A')

    prueba.usuario = User.objects.create_user('votante', 'votante@ejemplo.co', 'Festival-Prueba-2027')


def enviar_voto(cliente, votacion, opcion, confirmado=True):
    datos = {'opcion': opcion.pk}
    if confirmado:
        datos['confirmado'] = '1'
    return cliente.post(reverse('elecciones:votar', args=[votacion.pk]), datos, follow=True)


class VotoTests(TestCase):
    """Los casos CP-01 a CP-08 de la Entrega 3."""

    def setUp(self):
        crear_escenario_de_voto(self)
        self.client.force_login(self.usuario)

    def test_cp01_voto_valido_se_guarda_con_todos_sus_datos(self):
        respuesta = enviar_voto(self.client, self.cancion, self.cancion_a)
        self.assertContains(respuesta, 'Tu voto por Canción A quedó registrado.')
        voto = Voto.objects.get()
        self.assertEqual(
            (voto.usuario, voto.edicion, voto.categoria, voto.opcion),
            (self.usuario, self.edicion, self.musica, self.cancion_a),
        )

    def test_cp01_primero_pide_confirmar_y_no_guarda(self):
        respuesta = enviar_voto(self.client, self.cancion, self.cancion_a, confirmado=False)
        self.assertTemplateUsed(respuesta, 'elecciones/voto_confirmar.html')
        self.assertContains(respuesta, 'Canción A')
        self.assertFalse(Voto.objects.exists())

    def test_cp02_segundo_voto_en_la_misma_votacion_se_rechaza(self):
        enviar_voto(self.client, self.cancion, self.cancion_a)
        respuesta = enviar_voto(self.client, self.cancion, self.cancion_b)
        self.assertContains(respuesta, 'Ya votaste en esta categoría')
        self.assertEqual(Voto.objects.get().opcion, self.cancion_a)

    def test_cp02_segundo_voto_en_otro_subevento_de_la_categoria_se_rechaza(self):
        enviar_voto(self.client, self.cancion, self.cancion_a)
        respuesta = enviar_voto(self.client, self.conjunto, self.conjunto_a)
        self.assertContains(respuesta, 'Ya votaste en esta categoría')
        self.assertEqual(Voto.objects.count(), 1)

    def test_cp02_despues_de_votar_no_se_muestra_el_formulario(self):
        enviar_voto(self.client, self.cancion, self.cancion_a)
        respuesta = self.client.get(reverse('elecciones:detalle_votacion', args=[self.conjunto.pk]))
        self.assertFalse(respuesta.context['puede_votar'])
        self.assertContains(respuesta, 'Ya votaste en esta categoría')
        self.assertNotContains(respuesta, 'Continuar a la confirmación')

    def test_cp03_se_permite_votar_en_otra_categoria(self):
        enviar_voto(self.client, self.cancion, self.cancion_a)
        enviar_voto(self.client, self.vestuario, self.vestuario_a)
        self.assertEqual(Voto.objects.count(), 2)

    def test_cp03_otro_usuario_puede_votar_en_la_misma_categoria(self):
        enviar_voto(self.client, self.cancion, self.cancion_a)
        self.client.force_login(User.objects.create_user('otra', 'otra@ejemplo.co', 'Festival-Prueba-2027'))
        enviar_voto(self.client, self.cancion, self.cancion_a)
        self.assertEqual(Voto.objects.count(), 2)

    def test_cp04_sin_sesion_se_exige_ingresar(self):
        self.client.logout()
        url = reverse('elecciones:votar', args=[self.cancion.pk])
        respuesta = self.client.post(url, {'opcion': self.cancion_a.pk, 'confirmado': '1'})
        self.assertRedirects(respuesta, f"{reverse('cuentas:ingresar')}?next={url}")
        self.assertFalse(Voto.objects.exists())

    def test_cp04_despues_de_ingresar_vuelve_a_la_votacion(self):
        url = reverse('elecciones:votar', args=[self.cancion.pk])
        self.assertRedirects(self.client.get(url), reverse('elecciones:detalle_votacion', args=[self.cancion.pk]))

    def test_cp04_sin_token_csrf_se_rechaza(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.usuario)
        url = reverse('elecciones:votar', args=[self.cancion.pk])
        respuesta = cliente.post(url, {'opcion': self.cancion_a.pk, 'confirmado': '1'})
        self.assertEqual(respuesta.status_code, 403)
        self.assertFalse(Voto.objects.exists())

    def test_cp05_votacion_cerrada_o_proxima_se_rechaza(self):
        for votacion, opcion in ((self.cerrada, self.cerrada_a), (self.proxima, self.proxima_a)):
            respuesta = enviar_voto(self.client, votacion, opcion)
            self.assertContains(respuesta, 'Esta votación no está abierta')
        self.assertFalse(Voto.objects.exists())

    def test_cp05_categoria_inactiva_o_borrador_se_rechaza(self):
        Categoria.objects.filter(pk=self.musica.pk).update(activa=False)
        self.assertEqual(enviar_voto(self.client, self.cancion, self.cancion_a).status_code, 404)
        Votacion.objects.filter(pk=self.vestuario.pk).update(publicada=False)
        self.assertEqual(enviar_voto(self.client, self.vestuario, self.vestuario_a).status_code, 404)
        self.assertFalse(Voto.objects.exists())

    def test_cp06_opcion_de_otra_categoria_se_rechaza(self):
        respuesta = enviar_voto(self.client, self.cancion, self.vestuario_a)
        self.assertContains(respuesta, 'La opción enviada no pertenece a esta votación.')
        self.assertFalse(Voto.objects.exists())

    def test_cp06_opcion_de_otro_subevento_o_inexistente_se_rechaza(self):
        enviar_voto(self.client, self.cancion, self.conjunto_a)
        self.client.post(reverse('elecciones:votar', args=[self.cancion.pk]), {'opcion': 999999, 'confirmado': '1'})
        self.assertFalse(Voto.objects.exists())

    def test_cp07_mis_votos_muestra_solo_los_del_usuario(self):
        enviar_voto(self.client, self.cancion, self.cancion_a)
        Voto.registrar(User.objects.create_user('otra', 'otra@ejemplo.co', 'Festival-Prueba-2027'), self.vestuario_a)
        respuesta = self.client.get(reverse('elecciones:mis_votos'))
        self.assertContains(respuesta, 'Canción A')
        self.assertNotContains(respuesta, 'Vestuario A')

    def test_cp07_mis_votos_exige_iniciar_sesion(self):
        self.client.logout()
        respuesta = self.client.get(reverse('elecciones:mis_votos'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse('cuentas:ingresar'), respuesta.url)

    def test_cp08_administrador_consulta_los_votos_sin_poder_cambiarlos(self):
        voto = Voto.registrar(self.usuario, self.cancion_a)
        self.client.force_login(User.objects.create_superuser('admin-prueba', 'admin@ejemplo.co', 'Festival-Prueba-2027'))
        respuesta = self.client.get(reverse('admin:elecciones_voto_changelist'))
        self.assertContains(respuesta, 'votante')
        self.assertContains(respuesta, 'Canción A')
        self.assertEqual(self.client.get(reverse('admin:elecciones_voto_change', args=[voto.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('admin:elecciones_voto_add')).status_code, 403)
        self.assertEqual(self.client.post(reverse('admin:elecciones_voto_delete', args=[voto.pk]), {'post': 'yes'}).status_code, 403)
        self.assertTrue(Voto.objects.filter(pk=voto.pk).exists())


class ProteccionDuplicadosTests(TestCase):
    """La base de datos protege la regla aunque la validación del formulario no alcance a verlo."""

    def setUp(self):
        crear_escenario_de_voto(self)
        self.client.force_login(self.usuario)

    def test_mysql_rechaza_el_duplicado_directo(self):
        Voto.registrar(self.usuario, self.cancion_a)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Voto.registrar(self.usuario, self.conjunto_a)
        self.assertEqual(Voto.objects.count(), 1)

    def test_la_vista_maneja_el_error_de_integridad(self):
        # Simula la carrera: otra solicitud guardó el voto justo después de la validación
        Voto.registrar(self.usuario, self.cancion_a)
        with patch.object(Voto, 'de_usuario', return_value=None):
            respuesta = enviar_voto(self.client, self.cancion, self.cancion_b)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Ya votaste en esta categoría')
        self.assertEqual(Voto.objects.get().opcion, self.cancion_a)


class ConcurrenciaTests(TransactionTestCase):
    """CP-09: varias solicitudes simultáneas reales, cada una con su propia conexión a MySQL."""

    def test_cp09_solicitudes_simultaneas_dejan_un_solo_voto(self):
        crear_escenario_de_voto(self)
        solicitudes = 8
        barrera = threading.Barrier(solicitudes)
        estados = []

        def votar():
            try:
                cliente = Client()
                cliente.force_login(self.usuario)
                barrera.wait()  # todas salen al mismo tiempo
                url = reverse('elecciones:votar', args=[self.cancion.pk])
                respuesta = cliente.post(url, {'opcion': self.cancion_a.pk, 'confirmado': '1'})
                estados.append(respuesta.status_code)
            finally:
                connection.close()

        hilos = [threading.Thread(target=votar) for _ in range(solicitudes)]
        for hilo in hilos:
            hilo.start()
        for hilo in hilos:
            hilo.join()

        self.assertEqual(estados, [302] * solicitudes)  # ninguna termina en error del servidor
        self.assertEqual(Voto.objects.filter(usuario=self.usuario, categoria=self.musica).count(), 1)


class ApiCategoriasTests(TestCase):
    """CP-10: GET /api/categorias/."""

    def setUp(self):
        crear_escenario_de_voto(self)
        self.borrador = crear_votacion(self.musica, 'Votación borrador', -1, 5, publicada=False)
        Categoria.objects.create(edicion=self.edicion, nombre='Categoría oculta', activa=False)
        self.url = reverse('elecciones:api_categorias')

    def test_cp10_ruta_y_json_valido_con_datos_reales(self):
        self.assertEqual(self.url, '/api/categorias/')
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta['Content-Type'], 'application/json')
        datos = json.loads(respuesta.content)
        self.assertEqual(datos['total'], 3)
        musica = next(categoria for categoria in datos['categorias'] if categoria['nombre'] == 'Música')
        self.assertEqual(musica['edicion']['anio'], 2027)
        cancion = next(votacion for votacion in musica['votaciones'] if votacion['titulo'] == 'Canción favorita')
        self.assertEqual(cancion['estado'], 'abierta')
        self.assertEqual([opcion['nombre'] for opcion in cancion['opciones']], ['Canción A', 'Canción B'])

    def test_cp10_no_incluye_borradores_ni_categorias_inactivas(self):
        contenido = self.client.get(self.url).content.decode()
        self.assertNotIn('Votación borrador', contenido)
        self.assertNotIn('Categoría oculta', contenido)

    def test_solo_acepta_get(self):
        self.assertEqual(self.client.post(self.url).status_code, 405)

    def test_no_hace_una_consulta_por_cada_fila(self):
        with self.assertNumQueries(3):
            self.client.get(self.url)
