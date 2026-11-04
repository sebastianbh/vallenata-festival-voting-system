"""Pruebas de registro, inicio y cierre de sesión."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

# Contraseña ficticia solo para las pruebas automáticas (base de datos temporal)
CLAVE_PRUEBA = 'Festival-Prueba-2027'


class RegistroTests(TestCase):
    def datos(self, **cambios):
        datos = {
            'first_name': 'Ana Prueba', 'username': 'anaprueba', 'email': 'ana@ejemplo.co',
            'password1': CLAVE_PRUEBA, 'password2': CLAVE_PRUEBA, 'acepta_datos': 'on',
        }
        datos.update(cambios)
        return datos

    def test_registro_crea_usuario_e_inicia_sesion(self):
        respuesta = self.client.post(reverse('cuentas:registro'), self.datos(), follow=True)
        self.assertRedirects(respuesta, reverse('elecciones:inicio'))
        self.assertTrue(User.objects.filter(username='anaprueba', email='ana@ejemplo.co').exists())
        self.assertTrue(respuesta.context['user'].is_authenticated)

    def test_registro_exige_aceptar_datos(self):
        datos = self.datos()
        del datos['acepta_datos']
        respuesta = self.client.post(reverse('cuentas:registro'), datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(User.objects.exists())

    def test_correo_repetido_no_se_acepta(self):
        User.objects.create_user('otra', 'ana@ejemplo.co', CLAVE_PRUEBA)
        respuesta = self.client.post(reverse('cuentas:registro'), self.datos())
        self.assertContains(respuesta, 'Ya existe una cuenta con este correo.')


class VerClaveTests(TestCase):
    def test_los_campos_de_contrasena_tienen_el_boton_del_ojo(self):
        casos = [(reverse('cuentas:ingresar'), 1), (reverse('cuentas:registro'), 2)]
        for url, campos in casos:
            respuesta = self.client.get(url)
            self.assertContains(respuesta, 'password-field__toggle', count=campos)
            self.assertContains(respuesta, 'type="password"', count=campos)


class IngresoSalidaTests(TestCase):
    def setUp(self):
        User.objects.create_user('votante', 'votante@ejemplo.co', CLAVE_PRUEBA, first_name='Votante')

    def test_ingresar_y_salir(self):
        respuesta = self.client.post(reverse('cuentas:ingresar'), {'username': 'votante', 'password': CLAVE_PRUEBA}, follow=True)
        self.assertContains(respuesta, 'Salir (Votante)')

        respuesta = self.client.post(reverse('cuentas:salir'), follow=True)
        self.assertContains(respuesta, 'Cerraste sesión.')
        self.assertFalse(respuesta.context['user'].is_authenticated)

    def test_clave_incorrecta_muestra_error(self):
        respuesta = self.client.post(reverse('cuentas:ingresar'), {'username': 'votante', 'password': 'equivocada'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'notice--danger')
