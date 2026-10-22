# Guía paso a paso del proyecto Django

Bitácora de cómo se construyó el proyecto **Sistema Web de Votaciones – Festival de la Leyenda Vallenata 2027**, explicada de forma sencilla. Cada paso dice qué se hizo, para qué sirve y qué comandos se usaron.

---

## Ideas básicas antes de empezar

### Python, pip y Django no son lo mismo

| Pieza | Qué es | Parecido en PHP |
|---|---|---|
| **Python** | El lenguaje de programación. Se instala una sola vez en el computador. | PHP |
| **pip** | El programa que descarga librerías. Viene incluido con Python. | Composer |
| **Django** | El framework para hacer páginas web. Se instala con pip, dentro de cada proyecto. | Laravel |
| **Entorno virtual (`venv`)** | Una carpeta dentro del proyecto donde quedan Django y las demás librerías de ese proyecto. | La carpeta `vendor/` |
| **`requirements.txt`** | La lista de librerías y versiones que necesita el proyecto. | `composer.json` |
| **`manage.py`** | El archivo con el que se ejecutan los comandos del proyecto. | `php artisan` |

### ¿Qué es MVT?

Django organiza el código en tres partes (patrón **Modelo – Vista – Plantilla**):

- **Modelo**: describe los datos y se convierte en tablas de la base de datos (por ejemplo, una Votación).
- **Vista**: una función de Python que recibe la petición del navegador, busca los datos y decide qué mostrar.
- **Plantilla**: el archivo HTML que se le muestra al usuario, con los datos ya puestos.

### ¿Por qué Django 4.2 y no la versión más nueva?

Todo el equipo usa **XAMPP**, que trae **MariaDB 10.4** (XAMPP lo llama "MySQL"). Las versiones nuevas de Django (5.x) exigen MariaDB 10.5 o superior, y XAMPP no tiene una versión más nueva. Django 4.2 sí funciona con el XAMPP de siempre, así que nadie tiene que instalar otra base de datos. Es un proyecto para aprender y se priorizó que fuera sencillo.

### ¿Dónde está cada cosa en el repositorio?

- El repositorio del equipo es https://github.com/sebastianbh/vallenata-festival-voting-system. Se creó a partir del repositorio de la Entrega 1 (`jsanchez542-hub/vallenata-festival-voting-system`), con todo su historial.
- La **raíz del repositorio** es el prototipo HTML de la Entrega 1 (el que se ve en GitHub Pages).
- La carpeta **`django/`** es el proyecto real: el mismo diseño, ahora con Python y base de datos.

---

## Paso 1. Revisar el prototipo HTML

Se revisó el prototipo para decidir qué se reutiliza:

- **Se reutilizan tal cual**: los estilos (`assets/css`), las fuentes y las imágenes. Se copian a la carpeta `static/` de Django.
- **Se convierten en plantillas de Django**: las páginas HTML. El menú y el pie, que en el prototipo los dibuja JavaScript, pasan a un archivo común `base.html`.
- **No se usan**: el JavaScript que inventaba datos y los guardaba en el navegador, porque ahora los datos salen de la base de datos. Tampoco la carpeta `admin/`, porque Django trae su propio panel de administración.

## Paso 2. Decidir la estructura de carpetas

```
django/
├── manage.py            comandos del proyecto
├── requirements.txt     lista de librerías
├── .env.example         plantilla de la configuración privada (sin contraseñas)
├── .gitignore           archivos que NO se suben a GitHub
├── config/              configuración general y rutas principales
├── apps/
│   ├── cuentas/         registro, inicio y cierre de sesión
│   └── elecciones/      ediciones, categorías, votaciones y opciones
├── templates/           páginas HTML
├── static/              estilos, fuentes e imágenes del prototipo
└── docs/                esta guía y capturas para el informe
```

En Django, cada **app** es una parte del proyecto con un tema propio. Así el código queda ordenado.

## Paso 3. Instalar Python, crear el entorno virtual e instalar Django

### 3.1 Instalar Python (una sola vez por computador)

1. Descargar **Python 3.13** desde https://www.python.org/downloads/windows/ (instalador de 64 bits).
2. En la primera pantalla, **marcar la casilla "Add python.exe to PATH"**. Sin eso, la terminal no encuentra Python.
3. Al terminar, **cerrar y volver a abrir** VS Code o la terminal.
4. Comprobar que quedó instalado:

```powershell
python --version
```

Debe responder algo como `Python 3.13.x`.

### 3.2 Crear el entorno virtual

Desde la carpeta `django/`:

```powershell
python -m venv venv
```

Esto crea la carpeta `venv/`, donde quedarán las librerías del proyecto. Esa carpeta **no se sube a GitHub**: cada integrante la crea en su computador.

### 3.3 Activar el entorno virtual

```powershell
venv\Scripts\activate
```

Cuando está activo, la línea de la terminal empieza con **`(venv)`**. Mientras se vea así, `python` y `pip` usan las librerías de este proyecto. Para salir del entorno se escribe `deactivate`.

> **Si sale un error de "ejecución de scripts deshabilitada"**, ejecutar una sola vez el siguiente comando y volver a intentar:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

### 3.4 Instalar Django y las demás librerías

**La primera vez** (cuando se creó el proyecto) se instalaron así:

```powershell
python -m pip install --upgrade pip
pip install "Django>=4.2,<5.0" mysqlclient django-environ
pip freeze > requirements.txt
```

- `Django>=4.2,<5.0`: la versión más reciente de la serie 4.2.
- `mysqlclient`: permite que Django se comunique con MySQL/MariaDB.
- `django-environ`: lee la configuración privada (usuario y contraseña de la base de datos) desde un archivo `.env`.
- `pip freeze > requirements.txt`: guarda en un archivo la lista exacta de lo que quedó instalado.

**Los demás integrantes**, después de clonar el repositorio, solo necesitan:

```powershell
pip install -r requirements.txt
```

Ese comando lee la lista y les instala exactamente las mismas versiones.

### 3.5 Crear el proyecto Django

```powershell
django-admin startproject config .
```

Crea `manage.py` y la carpeta `config/`. El punto del final significa "créalo en esta misma carpeta".

| Archivo | Para qué sirve |
|---|---|
| `manage.py` | Ejecutar comandos del proyecto |
| `config/settings.py` | La configuración: apps instaladas, base de datos, idioma, etc. |
| `config/urls.py` | Las rutas: qué página se muestra en cada dirección |
| `config/wsgi.py` y `config/asgi.py` | Para publicar en un servidor real; no se tocan |

### 3.6 Comprobar que funciona

```powershell
python manage.py check
python manage.py runserver
```

- `check` revisa que no haya errores de configuración. Debe decir *"System check identified no issues"*.
- `runserver` enciende un servidor de prueba. Al abrir http://127.0.0.1:8000 en el navegador aparece la página de bienvenida de Django (un cohete).
- Para apagar el servidor se presiona `Ctrl + C`.

> No se usa el Apache de XAMPP: Django trae su propio servidor para desarrollo. De XAMPP solo se usa MySQL.

## Paso 4. Conectar Django con MySQL usando un archivo `.env`

### 4.1 La configuración se partió en dos archivos

El archivo `config/settings.py` que crea Django se reemplazó por una carpeta:

```
config/settings/
├── base.py    lo que es igual en cualquier computador o servidor
└── local.py   lo propio de desarrollo: DEBUG activado y direcciones permitidas
```

`local.py` empieza con `from .base import *`, es decir, "trae todo lo de base.py" y solo agrega o cambia lo de desarrollo. Si algún día el proyecto se publica en un servidor, se crea un `produccion.py` sin tocar los demás.

`manage.py`, `wsgi.py` y `asgi.py` se cambiaron para que usen `config.settings.local`.

En `base.py` también quedó:
- **Idioma español de Colombia** (`es-co`): el panel de administración y los mensajes de error salen en español.
- **Zona horaria de Bogotá** (`America/Bogota`): las fechas de apertura y cierre de las votaciones se muestran con la hora de Colombia.
- **La carpeta `templates/`** como lugar de las plantillas HTML del proyecto.

### 4.2 Los datos privados van en `.env`

Igual que en Laravel, la clave secreta y los datos de conexión no se escriben en el código. Se guardan en un archivo `.env` que **no se sube a GitHub**. La librería `django-environ` lo lee al arrancar.

Hay dos archivos:

| Archivo | ¿Se sube a GitHub? | Para qué |
|---|---|---|
| `.env.example` | Sí | Plantilla con los nombres de las variables, sin datos reales |
| `.env` | **No** | La configuración real de cada integrante |

Variables que usa el proyecto:

| Variable | Valor con XAMPP | Qué es |
|---|---|---|
| `SECRET_KEY` | Una clave larga y aleatoria | Django la usa para firmar las sesiones. Cada integrante genera la suya |
| `DEBUG` | `True` | Muestra errores detallados (solo en desarrollo) |
| `DB_NAME` | `votaciones_festival` | Nombre de la base de datos |
| `DB_USER` | `root` | Usuario de MySQL |
| `DB_PASSWORD` | *(vacío)* | XAMPP trae `root` sin contraseña |
| `DB_HOST` | `127.0.0.1` | El propio computador |
| `DB_PORT` | `3306` | Puerto de MySQL en XAMPP |

**Cada integrante, después de clonar**, hace esto desde la carpeta `django/`:

```powershell
copy .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

El segundo comando imprime una clave aleatoria. Se copia y se pega en `.env`, en la línea `SECRET_KEY=`.

> **¿Por qué se borró el `settings.py` original?** Traía una clave secreta escrita en el código. Si se hubiera subido a GitHub, cualquiera podría verla, aunque después se borrara (queda en el historial). Por eso se generó una nueva y quedó solo en `.env`.

### 4.3 La base de datos

1. Encender **MySQL** en el panel de XAMPP.
2. Crear la base en phpMyAdmin (http://localhost/phpmyadmin): pestaña *Bases de datos*, nombre `votaciones_festival` y cotejamiento `utf8mb4_unicode_ci`. O con este comando SQL:

```sql
CREATE DATABASE votaciones_festival CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

`utf8mb4` permite guardar tildes, eñes y cualquier otro carácter sin que se dañen.

En la configuración también se activó el **modo estricto** de MySQL: si llega un dato que no cabe o es inválido, MySQL da un error en vez de recortarlo sin avisar.

### 4.4 Comprobar la conexión

```powershell
python manage.py check --database default
```

Además de revisar la configuración, se conecta a MySQL. Si responde *"System check identified no issues"*, la conexión funciona. Las tablas todavía no existen; se crean en el paso 5.

## Paso 5. Crear los modelos y las tablas

### 5.1 Crear la app `elecciones`

Un proyecto Django se divide en **apps**: carpetas con un tema propio, cada una con sus modelos, vistas, rutas y configuración del panel. Todas las apps del proyecto van dentro de `apps/`.

```powershell
python manage.py startapp elecciones apps\elecciones
```

Después de crearla, hay que **registrarla** en `config/settings/base.py`, en la lista `INSTALLED_APPS`, con el nombre `'apps.elecciones'`. Si no está en esa lista, Django no la tiene en cuenta.

### 5.2 Instalar Pillow

El modelo `Opcion` tiene un campo de imagen, y Django exige la librería **Pillow** para manejar imágenes.

```powershell
pip install Pillow
pip freeze > requirements.txt
```

Las imágenes que se suben desde el panel se guardan en la carpeta `media/`, que no se sube a GitHub.

### 5.3 Los modelos

Un **modelo** es una clase de Python que describe una tabla. Django crea la tabla a partir de ella (como los modelos de Eloquent en Laravel). Están en `apps/elecciones/models.py`.

```
Edicion  ──<  Categoria  ──<  Votacion  ──<  Opcion
```

Cada flecha significa "una edición tiene muchas categorías", "una categoría tiene muchas votaciones", y así sucesivamente.

| Modelo | Campos |
|---|---|
| **Edicion** | número, año, nombre, lugar, fecha de inicio, fecha de fin, activa, mostrar en portada |
| **Categoria** | edición, nombre, descripción, activa |
| **Votacion** | categoría, título, descripción, fecha de apertura, fecha de cierre, publicada |
| **Opcion** | votación, nombre, descripción, imagen (opcional), orden |

Algunas ideas importantes:

- **`ForeignKey`** es la relación "pertenece a". En la tabla se convierte en una columna como `edicion_id`.
- **`related_name`** permite consultar al revés: `edicion.categorias.all()` trae todas las categorías de una edición.
- **`PROTECT`** impide borrar una edición que todavía tiene categorías (o una categoría que tiene votaciones), para no borrar información por accidente. **`CASCADE`** hace que, al borrar una votación, se borren también sus opciones.
- **El estado de una votación no se guarda**: se calcula con las fechas cada vez que se consulta.
  - **Próxima**: todavía no llega la fecha de apertura.
  - **Abierta**: ya abrió y no ha cerrado.
  - **Cerrada**: ya pasó la fecha de cierre.

  Así nunca queda una votación "abierta" con la fecha vencida. El campo **publicada** sirve para esconder una votación mientras se prepara.

### 5.4 Crear y aplicar las migraciones

Una **migración** es un archivo con las instrucciones para crear o cambiar tablas, como en Laravel. La diferencia es que Django la escribe solo, leyendo los modelos.

```powershell
python manage.py makemigrations
python manage.py migrate
```

- `makemigrations` revisa los modelos y crea el archivo de migración (`apps/elecciones/migrations/0001_initial.py`). Todavía no toca la base de datos.
- `migrate` ejecuta las migraciones pendientes y crea las tablas en MySQL.

Además de las 4 tablas del proyecto (`elecciones_edicion`, `elecciones_categoria`, `elecciones_votacion` y `elecciones_opcion`), Django crea las suyas: usuarios (`auth_user`), permisos, sesiones (`django_session`), el historial del panel y `django_migrations`, donde anota qué migraciones ya se aplicaron.

**Ejemplo de un cambio posterior.** Más adelante se agregó a `Edicion` el campo **"mostrar en portada"**, para que la administración elija qué edición sale en el banner del inicio. Al guardar una edición marcada, las demás se desmarcan solas, y si ninguna está marcada se muestra la más reciente. Como se cambió el modelo, se creó una segunda migración (`0002_edicion_en_portada.py`), que solo agrega esa columna a la tabla.

> **Regla de oro:** cada vez que se cambia un modelo, se ejecuta `makemigrations` y luego `migrate`. Los archivos de migración **sí se suben a GitHub**, para que los compañeros solo tengan que ejecutar `migrate`.

## Paso 6. Panel de administración (Django Admin)

Django trae un panel de administración listo para usar. Solo hay que decirle qué modelos mostrar y cómo; eso se hace en `apps/elecciones/admin.py`.

| Opción | Qué hace |
|---|---|
| `list_display` | Las columnas que se ven en la lista |
| `list_filter` | Los filtros de la barra lateral (por edición, por estado, etc.) |
| `search_fields` | Los campos en los que busca el buscador |
| `inlines` | Permite editar registros relacionados en la misma pantalla |

Con los *inlines*, las **categorías se crean desde la pantalla de la edición** y las **opciones desde la pantalla de la votación**, sin cambiar de página.

Para entrar al panel se necesita un **superusuario** (un usuario con todos los permisos):

```powershell
python manage.py createsuperuser
```

Pide usuario, correo y contraseña. **La contraseña no se ve mientras se escribe**: es normal. No se guarda en ningún archivo del proyecto, solo en la base de datos y cifrada.

Luego se entra a http://127.0.0.1:8000/admin.

## Paso 7. Datos de prueba

Para no tener que crear todo a mano, el proyecto trae un **comando propio** que carga datos ficticios:

```powershell
python manage.py cargar_datos_prueba
```

Carga 2 ediciones (60.ª de 2027 y 59.ª de 2026), 4 categorías, 6 votaciones y sus opciones. Las fechas se calculan desde el día en que se ejecuta, así que siempre hay votaciones **abiertas**, **próximas** y **cerradas**, y además un **borrador** que no debe verse en el sitio público.

Se puede ejecutar varias veces: actualiza lo que ya existe en vez de duplicarlo.

El código está en `apps/elecciones/management/commands/cargar_datos_prueba.py`. Django reconoce como comando cualquier archivo que esté en esa ruta (`management/commands/`) dentro de una app.

## Paso 8. Registro, inicio y cierre de sesión

Se creó la app `cuentas`. Usa el sistema de usuarios que ya trae Django (tabla `auth_user`, contraseñas cifradas), así que no hace falta un modelo propio.

| Archivo | Qué contiene |
|---|---|
| `apps/cuentas/forms.py` | El formulario de registro: parte del `UserCreationForm` de Django y le agrega nombre, correo y la casilla de tratamiento de datos |
| `apps/cuentas/views.py` | El inicio y el cierre de sesión usan las vistas de Django (`LoginView` y `LogoutView`); el registro es una función propia |
| `apps/cuentas/urls.py` | Las rutas `/cuentas/ingresar/`, `/cuentas/salir/` y `/cuentas/registro/` |
| `templates/cuentas/` | Las pantallas, con el diseño de `sign-in.html` y `sign-up.html` del prototipo |

Algunos detalles:
- Al crear la cuenta, el usuario queda con la sesión iniciada.
- No se permiten dos cuentas con el mismo correo.
- **Cerrar sesión se hace con un botón que envía un formulario (POST)** y no con un enlace normal. Así otra página no puede cerrar tu sesión con solo poner un enlace oculto. Es lo que recomienda Django.
- Todos los formularios llevan `{% csrf_token %}`, una protección de Django contra envíos falsificados desde otros sitios.

## Paso 9. Plantillas y páginas públicas

### Archivos estáticos

Los estilos, las fuentes y las imágenes del prototipo se copiaron a `static/`. En las plantillas se enlazan con la etiqueta `{% static %}`:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/tokens.css' %}">
```

### Herencia de plantillas

`templates/base.html` tiene lo que comparten todas las páginas: el `<head>`, el aviso académico, el menú y el pie. Cada página **hereda** de ella y solo rellena sus bloques (como `@extends` y `@section` en Blade):

```html
{% extends 'base.html' %}

{% block titulo %}Ediciones{% endblock %}

{% block contenido %}
  ... contenido de la página ...
{% endblock %}
```

Las partes que se repiten (la fila de una votación, la etiqueta de estado, un campo de formulario) están en `templates/parciales/` y se insertan con `{% include %}`.

### Las páginas

| Dirección | Vista | Qué muestra |
|---|---|---|
| `/` | `inicio` | Portada: la edición actual, las votaciones abiertas y las categorías |
| `/ediciones/` | `lista_ediciones` | Todas las ediciones activas |
| `/ediciones/<id>/` | `detalle_edicion` | Las categorías de una edición |
| `/categorias/<id>/` | `detalle_categoria` | Las votaciones de una categoría |
| `/votaciones/<id>/` | `detalle_votacion` | Una votación con sus opciones |

Cada **vista** (`apps/elecciones/views.py`) consulta MySQL con el ORM de Django y le pasa los datos a su plantilla. Por ejemplo:

```python
def detalle_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk, activa=True)
    votaciones = categoria.votaciones.filter(publicada=True)
    return render(request, 'elecciones/categoria_detalle.html', {'categoria': categoria, 'votaciones': votaciones})
```

`get_object_or_404` busca el registro y, si no existe o no está visible, muestra la página "No encontrado" (error 404).

**Solo se muestra lo que la administración dejó visible**: ediciones y categorías activas, y votaciones publicadas.

El menú cambia según el usuario: muestra **Ingresar / Crear cuenta** si no ha iniciado sesión, y **Salir** si ya inició. A los administradores también les muestra el enlace al panel. En la plantilla se hace así:

```html
{% if user.is_authenticated %} ... Salir ... {% else %} ... Ingresar ... {% endif %}
```

## Pruebas automáticas

En `apps/elecciones/tests.py` y `apps/cuentas/tests.py` hay pruebas que revisan solas que el sistema funcione. Por ejemplo: que las páginas abran, que un borrador no se vea, que el registro cree el usuario y que el inicio y el cierre de sesión funcionen.

```powershell
python manage.py test
```

Django crea una base de datos temporal (`test_votaciones_festival`), ejecuta las pruebas y la borra al terminar. Si todo está bien, termina diciendo **OK**.

---

## Problemas comunes

### XAMPP: "MySQL shutdown unexpectedly"

**Qué pasa:** MySQL no enciende desde el panel de XAMPP y aparece este mensaje.

**Causa más común:** se apagó el computador o se cerró XAMPP sin detener MySQL primero. Eso puede dañar las tablas internas donde MySQL guarda los usuarios y permisos, y entonces se cierra apenas intenta leerlas.

**Cómo evitarlo:** antes de apagar el computador o cerrar XAMPP, presionar siempre **Stop** en MySQL.

**Cómo se arregló en este proyecto:** las tablas dañadas eran `db`, `proxies_priv` y `columns_priv` (en `C:\xampp\mysql\data\mysql\`). Con MySQL detenido, se guardó una copia de sus archivos y se reemplazaron por las originales que XAMPP trae en `C:\xampp\mysql\backup\mysql\`. Las bases de datos de los proyectos no se tocan, porque están en otras carpetas.

---

## Resumen de comandos

| Comando | Qué hace |
|---|---|
| `python --version` | Muestra la versión de Python instalada |
| `python -m venv venv` | Crea el entorno virtual |
| `venv\Scripts\activate` | Activa el entorno virtual |
| `deactivate` | Sale del entorno virtual |
| `pip install -r requirements.txt` | Instala las librerías del proyecto |
| `pip freeze > requirements.txt` | Guarda la lista de librerías instaladas |
| `python manage.py check` | Revisa que la configuración esté bien |
| `python manage.py runserver` | Enciende el servidor en http://127.0.0.1:8000 |
| `copy .env.example .env` | Crea el archivo de configuración privada a partir de la plantilla |
| `python -c "import secrets; print(secrets.token_urlsafe(50))"` | Genera una clave secreta aleatoria para `SECRET_KEY` |
| `python manage.py check --database default` | Revisa la configuración y prueba la conexión con MySQL |
| `python manage.py startapp nombre apps\nombre` | Crea una app nueva dentro de `apps/` |
| `python manage.py makemigrations` | Crea los archivos de migración a partir de los modelos |
| `python manage.py migrate` | Aplica las migraciones: crea o cambia las tablas en MySQL |
| `python manage.py showmigrations` | Muestra qué migraciones están aplicadas (`[X]`) y cuáles faltan (`[ ]`) |
| `python manage.py createsuperuser` | Crea un usuario administrador para entrar a `/admin` |
| `python manage.py cargar_datos_prueba` | Carga los datos de prueba ficticios |
| `python manage.py test` | Ejecuta las pruebas automáticas |
