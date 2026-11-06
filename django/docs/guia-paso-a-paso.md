# Guía del proyecto Django

Guía única del equipo para el **Sistema Web de Votaciones – Festival de la Leyenda Vallenata 2027**. Se actualiza en cada entrega: no hay otra versión en Word ni en otro archivo.

| Si necesitas… | Ve a |
|---|---|
| Dejar listo tu computador por primera vez | Parte 1 |
| Trabajar en el día a día o traer los cambios del equipo | Parte 2 |
| Entender cómo se construyó el proyecto | Parte 3 |
| Revisar la Entrega 3, grabar el video y llenar el PDF | Parte 4 |
| Resolver un error | Problemas comunes |

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

# Parte 1. Preparar tu computador

Todo se hace en Windows, con la terminal de VS Code. Sigue los pasos en orden.

| Programa | Para qué | Dónde se consigue |
|---|---|---|
| Python 3.13 | El lenguaje del proyecto | python.org/downloads/windows |
| XAMPP | Su MySQL (MariaDB) y phpMyAdmin | apachefriends.org |
| Git | Descargar el proyecto y subir cambios | git-scm.com |
| VS Code | Editor de código | code.visualstudio.com |

Django no se instala a mano: se instala en el paso 1.4 con un comando. Django trae su propio servidor, así que no usa el Apache de XAMPP. Apache solo hace falta para abrir phpMyAdmin.

## 1.1 Instalar Python

1. Descarga **Python 3.13** (64 bits) desde https://www.python.org/downloads/windows/. **No uses la 3.14 ni una más nueva**: Django 4.2 falla con ellas en el panel de administración.
2. En la primera pantalla del instalador, **marca la casilla "Add python.exe to PATH"**. Es lo más importante de todo el proceso.
3. Haz clic en *Install Now*.
4. Cierra VS Code por completo y vuelve a abrirlo. La terminal solo reconoce a Python después de reiniciarla.
5. Abre una terminal (*Terminal → Nueva terminal*) y comprueba:

```powershell
python --version
```

Debe responder algo como `Python 3.13.x`.

## 1.2 Descargar el proyecto

Usa https://github.com/sebastianbh/vallenata-festival-voting-system y no el repositorio de la Entrega 1 (`jsanchez542-hub`), que solo tiene el prototipo HTML.

**Si no lo tienes en tu computador**, abre la terminal en la carpeta de tus trabajos y ejecuta:

```powershell
git clone https://github.com/sebastianbh/vallenata-festival-voting-system.git votaciones-festival
cd votaciones-festival
```

**Si ya lo habías clonado**, no lo clones de nuevo. Trae lo último:

```powershell
git checkout main
git pull
```

Luego abre la carpeta en VS Code (*Archivo → Abrir carpeta*). Debe existir la carpeta `django/`, con `manage.py` y `requirements.txt` adentro. **Todos los comandos de aquí en adelante se ejecutan dentro de `django/`.**

Para descargar no hace falta permiso, porque el repositorio es público. Para subir cambios, pídele al dueño (`sebastianbh`) que te invite desde *Settings → Collaborators* y acepta la invitación que te llega por correo.

## 1.3 Crear y activar el entorno virtual

El entorno virtual es una carpeta llamada `venv` donde quedan Django y las demás librerías de este proyecto. No se sube a GitHub: cada integrante crea la suya.

```powershell
cd django
py -3.13 -m venv venv
venv\Scripts\activate
```

`py -3.13` usa Python 3.13 aunque tengas otras versiones instaladas. Para comprobarlo, con el entorno activo, `python --version` debe decir `3.13.x`.

Cuando está activo, la línea de la terminal empieza con **`(venv)`**. En cada terminal nueva hay que activarlo otra vez. Para salir se escribe `deactivate`.

> **Si sale "la ejecución de scripts está deshabilitada"**, ejecuta una sola vez este comando y vuelve a activar:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

## 1.4 Instalar Django y las librerías

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Esto instala exactamente las mismas versiones que usa el resto del equipo.

## 1.5 Crear la base de datos

1. En el panel de XAMPP, presiona **Start** en **MySQL** y en **Apache**. Los dos deben quedar en verde. Apache es necesario para abrir phpMyAdmin; Django funciona solo con MySQL.
2. Entra a http://localhost/phpmyadmin, pestaña **SQL**, pega esto y presiona *Continuar*:

```sql
CREATE DATABASE votaciones_festival CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

`utf8mb4` permite guardar tildes, eñes y cualquier otro carácter sin que se dañen. La base queda vacía: Django crea las tablas en el paso 1.7.

## 1.6 Crear tu archivo `.env`

Igual que en Laravel, la clave secreta y los datos de conexión van en un archivo `.env` que **nunca se sube a GitHub**.

```powershell
copy .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

El segundo comando imprime una clave. Abre `.env` y pégala en la línea `SECRET_KEY=`. El archivo queda así, con tu clave:

```
SECRET_KEY=aqui-va-la-clave-larga-que-generaste
DEBUG=True
DB_NAME=votaciones_festival
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
```

`DB_PASSWORD` va vacío porque XAMPP trae el usuario `root` sin contraseña.

## 1.7 Crear las tablas y cargar los datos de prueba

```powershell
python manage.py check --database default
python manage.py migrate
python manage.py cargar_datos_prueba
```

- `check` comprueba la conexión. Debe decir *"System check identified no issues"*.
- `migrate` crea las tablas. Verás líneas que terminan en `OK` y 15 tablas en phpMyAdmin.
- `cargar_datos_prueba` es el *seeder*, como `php artisan db:seed`. Debe responder: *"Datos de prueba cargados: 2 ediciones, 4 categorías, 7 votaciones y 22 opciones."*

| Qué se carga | Detalle |
|---|---|
| 2 ediciones | La 60.ª (2027) y la 59.ª (2026) |
| 4 categorías | Música, Piloneras y vestuario, Presentaciones, y Música de 2026 |
| 7 votaciones | 3 abiertas, 1 próxima, 2 cerradas y 1 borrador, que no se ve en el sitio público |
| 22 opciones | Nombres ficticios: "Canción A", "Conjunto B", etc. |

Se puede ejecutar todas las veces que quieras: no duplica nada. Las fechas se calculan desde el día en que lo ejecutas, así que hazlo antes de una presentación o de grabar el video.

## 1.8 Crear tu superusuario

| Tipo de usuario | Cómo se crea | Qué puede hacer |
|---|---|---|
| Votante | Él mismo, con **Crear cuenta** en el sitio | Ver las votaciones, votar y consultar sus votos |
| Superusuario | Tú, con un comando | Lo anterior, y entrar a `/admin` para administrar los datos y consultar todos los votos |

```powershell
python manage.py createsuperuser
```

Responde usuario, correo y contraseña. **Al escribir la contraseña no se ve nada**: es normal. Si dice que es demasiado común, responde `N` y elige otra. No la escribas en ningún archivo del proyecto. El superusuario no viene en los datos de prueba porque las contraseñas nunca se guardan en el repositorio.

## 1.9 Encender el proyecto y comprobar

```powershell
python manage.py test
python manage.py runserver
```

`test` debe terminar en `OK`. Cuando `runserver` diga *"Starting development server at http://127.0.0.1:8000/"*, abre esa dirección en el navegador. Deja la terminal abierta mientras trabajas: Django se reinicia solo al guardar un archivo. Para apagarlo, **Ctrl + C**.

Tu entorno quedó listo si:

- [ ] En el inicio se ven las votaciones abiertas y las categorías.
- [ ] **Crear cuenta** funciona: al terminar, el menú dice *Salir (tu nombre)* y muestra *Mis votos*.
- [ ] En `/admin` entras con tu superusuario y ves Ediciones, Categorías, Votaciones, Opciones y Votos.
- [ ] http://127.0.0.1:8000/api/categorias/ muestra el JSON.

---

# Parte 2. El día a día

## Cada vez que vayas a trabajar

1. En XAMPP, **Start** en MySQL.
2. Trae los cambios del equipo y activa el entorno:

```powershell
git checkout main
git pull
cd django
venv\Scripts\activate
```

3. Según lo que haya cambiado:

| Si… | Ejecuta |
|---|---|
| Alguien agregó librerías (cambió `requirements.txt`) | `pip install -r requirements.txt` |
| Alguien cambió los modelos, o sale el aviso *unapplied migration(s)* | `python manage.py migrate` |
| Cambiaron los datos de prueba, o las votaciones ya cerraron por las fechas | `python manage.py cargar_datos_prueba` |

4. Enciende el servidor: `python manage.py runserver`.
5. Al terminar: **Ctrl + C** en la terminal y **Stop** en MySQL antes de apagar el computador. Si lo apagas con MySQL encendido, sus tablas internas se pueden dañar.

## Para subir cambios

No se trabaja directo sobre `main`. Se crea una rama, se sube y se hace un *pull request* en GitHub:

```powershell
git checkout -b feature/nombre-del-cambio
git add .
git commit -m "feat: descripcion del cambio"
git push -u origin feature/nombre-del-cambio
```

`.gitignore` ya evita que se suban `.env` y `venv`.

---

# Parte 3. Cómo se construyó


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
└── docs/                esta guía
```

En Django, cada **app** es una parte del proyecto con un tema propio. Así el código queda ordenado.

## Paso 3. Instalar Django y crear el proyecto

### 3.1 Instalar las librerías

Python y el entorno virtual se prepararon como en los pasos 1.1 y 1.3. **La primera vez**, cuando se creó el proyecto, las librerías se instalaron así:

```powershell
python -m pip install --upgrade pip
pip install "Django>=4.2,<5.0" mysqlclient django-environ
pip freeze > requirements.txt
```

- `Django>=4.2,<5.0`: la versión más reciente de la serie 4.2.
- `mysqlclient`: permite que Django se comunique con MySQL/MariaDB.
- `django-environ`: lee la configuración privada (usuario y contraseña de la base de datos) desde un archivo `.env`.
- `pip freeze > requirements.txt`: guarda en un archivo la lista exacta de lo que quedó instalado. Los demás integrantes la usan en el paso 1.4.

### 3.2 Crear el proyecto Django

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

### 3.3 Comprobar que funciona

```powershell
python manage.py check
python manage.py runserver
```

- `check` revisa que no haya errores de configuración. Debe decir *"System check identified no issues"*.
- `runserver` enciende un servidor de prueba. Al abrir http://127.0.0.1:8000 en el navegador aparece la página de bienvenida de Django (un cohete).
- Para apagar el servidor se presiona `Ctrl + C`.

> Django trae su propio servidor para desarrollo, así que no usa el Apache de XAMPP. Apache solo hace falta para abrir phpMyAdmin (http://localhost/phpmyadmin).

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

Cada integrante crea su propio `.env` como se explica en el paso 1.6.

> **¿Por qué se borró el `settings.py` original?** Traía una clave secreta escrita en el código. Si se hubiera subido a GitHub, cualquiera podría verla, aunque después se borrara (queda en el historial). Por eso se generó una nueva y quedó solo en `.env`.

### 4.3 La base de datos

La base se crea como se explica en el paso 1.5.

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

Carga 2 ediciones (60.ª de 2027 y 59.ª de 2026), 4 categorías, 7 votaciones y sus opciones. Las fechas se calculan desde el día en que se ejecuta, así que siempre hay votaciones **abiertas**, **próximas** y **cerradas**, y además un **borrador** que no debe verse en el sitio público.

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
- **El botón del ojo** permite ver la contraseña mientras se escribe, en Ingresar y en Crear cuenta. El botón está en `templates/parciales/_campo.html`, que lo agrega a cualquier campo de tipo contraseña. El archivo `static/js/ver-clave.js` cambia el campo de `password` a `text` y viceversa, y `static/css/components.css` le da el estilo. La contraseña se envía igual: solo cambia cómo se ve en pantalla.

## Paso 9. Plantillas y páginas públicas

### Archivos estáticos

Los estilos, las fuentes y las imágenes del prototipo se copiaron a `static/`. En las plantillas se enlazan con la etiqueta `{% static %}`:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/tokens.css' %}">
```

En `base.html` los CSS y JS terminan en `?v=2`. El navegador guarda una copia de estos archivos y a veces no los vuelve a descargar aunque cambien. Por ejemplo, al agregar el botón del ojo, el botón quedaba debajo del campo porque el navegador seguía usando el CSS viejo. Cada vez que se cambie un CSS o un JS, hay que subir ese número en `base.html` (`?v=3`, `?v=4`…), y así todos los navegadores descargan la versión nueva.

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

## Paso 10. Módulo de votos (Entrega 3)

**Quien descarga estos cambios debe ejecutar**, dentro de `django/` y con el entorno activo:

```powershell
python manage.py migrate
python manage.py cargar_datos_prueba
```

`migrate` crea la tabla `elecciones_voto`. El seeder deja abierta una votación en otra categoría, necesaria para demostrar el voto en una categoría diferente.

### El modelo `Voto` y la regla de unicidad

El voto une al usuario con la edición, la categoría y la opción. La regla central se le entrega a MySQL como una restricción (en Laravel sería `$table->unique([...])` en la migración):

```python
models.UniqueConstraint(fields=['usuario', 'edicion', 'categoria'], name='un_voto_por_usuario_categoria_edicion')
```

### Las dos capas de protección

1. **El formulario** (`apps/elecciones/forms.py`) revisa antes de guardar: que la opción sea de esta votación, que la votación esté abierta y que el usuario no haya votado en la categoría. Da mensajes claros.
2. **MySQL** es la protección final. Si llegan dos solicitudes al mismo tiempo, las dos pueden pasar la revisión del formulario, porque ninguna ve todavía el voto de la otra. Al guardar, MySQL acepta una y a la otra le responde con un error. La vista lo atrapa:

```python
try:
    with transaction.atomic():
        Voto.registrar(request.user, opcion)
except IntegrityError:
    messages.error(request, 'Ya votaste en esta categoría: ...')
```

`transaction.atomic()` hace que el error afecte solo a ese intento de guardar y no deje la conexión en mal estado.

### El recorrido del voto

| Paso | Qué pasa |
|---|---|
| 1 | En `/votaciones/<id>/` el usuario elige una opción y envía el formulario por POST |
| 2 | La vista `votar` valida y muestra la confirmación. Todavía no guarda nada |
| 3 | Al confirmar, llega otro POST con `confirmado`; la vista valida de nuevo y guarda |
| 4 | Redirige a `/mis-votos/` con el mensaje de éxito |

- `@login_required` envía a la página de ingreso a quien no ha iniciado sesión (en Laravel, el middleware `auth`).
- `{% csrf_token %}` protege los formularios (en Laravel, `@csrf`).
- En el panel de administración los votos son de solo lectura: `VotoAdmin` niega agregar, cambiar y borrar.

### La API

`GET /api/categorias/` está en `apps/elecciones/api.py`. Consulta MySQL, arma diccionarios de Python y los devuelve con `JsonResponse`. No necesita librerías adicionales. `prefetch_related` evita hacer una consulta por cada fila: siempre son 3 consultas, sin importar cuántos datos haya.

## Pruebas automáticas

En `apps/elecciones/tests.py` y `apps/cuentas/tests.py` hay pruebas que revisan solas que el sistema funcione. Por ejemplo: que las páginas abran, que un borrador no se vea, que el registro cree el usuario y que el inicio y el cierre de sesión funcionen.

```powershell
python manage.py test
```

Django crea una base de datos temporal (`test_votaciones_festival`), ejecuta las pruebas y la borra al terminar. Si todo está bien, termina diciendo **OK**.

Si una ejecución anterior se interrumpió, Django avisa que la base temporal ya existe y pregunta si la borra: se responde `yes`. Es solo la base temporal, no la del proyecto.

Las pruebas `test_cp01` a `test_cp10` corresponden a los casos de la Entrega 3 (ver la Parte 4). Para ver cada una por su nombre:

```powershell
python manage.py test apps.elecciones -v 2
```

---

# Parte 4. Entrega 3: revisar, demostrar y documentar

## Qué se agregó y cómo revisarlo

Antes de revisar, ejecuta `migrate` y `cargar_datos_prueba`, y crea una **cuenta nueva** en `/cuentas/registro/`, porque un voto no se puede deshacer.

Los números de las direcciones (por ejemplo `/votaciones/3/`) cambian en cada computador, así que las votaciones se buscan **por su nombre**: **Ediciones → 60.ª edición →** la categoría **→** la votación.

| # | Qué es nuevo | Dónde | Cómo revisarlo | Debe pasar |
|---|---|---|---|---|
| 1 | Elegir una opción | *Canción favorita del público* (Música) | Con sesión iniciada, elige una opción y pulsa **Continuar a la confirmación** | Se abre la confirmación. Todavía no se guarda nada |
| 2 | Confirmar el voto | Página de confirmación | Pulsa **Cambiar opción** y regresa. Luego vuelve a elegir y pulsa **Confirmar voto** | Te lleva a **Mis votos** con «Tu voto por … quedó registrado» |
| 3 | Mis votos (menú nuevo) | `/mis-votos/` | Abre el menú **Mis votos** | Lista tu categoría, opción, votación, edición y fecha |
| 4 | Un voto por categoría | *Agrupación favorita del público* (Música) | Abre el otro subevento de Música | No hay formulario: dice «Ya votaste en esta categoría por …» |
| 5 | Otra categoría sí se permite | *Vestuario más destacado* (Piloneras y vestuario) | Vota en *Vestuario más destacado* | Se registra, y **Mis votos** muestra dos filas |
| 6 | Rechazo del duplicado | Dos pestañas | Con otra cuenta, abre la misma votación en dos pestañas. Vota en una; en la otra, elige otra opción y continúa | Aviso rojo «Ya votaste en esta categoría» |
| 7 | Exige sesión | *Canción favorita del público* | Sal de tu cuenta y abre la votación | Pide **Ingresar para votar** y, al ingresar, vuelve a la votación |
| 8 | Votaciones no abiertas | *Presentación más recordada* y *Grupo de piloneras favorito* | Abre la cerrada y la próxima | No ofrecen formulario |
| 9 | Votos en el admin | `/admin/elecciones/voto/` | Entra con el superusuario y abre un voto | Se ven los datos, sin botones de agregar, guardar ni borrar |
| 10 | API GET | `/api/categorias/` | Ábrela en el navegador | JSON con tildes, categorías, votaciones y opciones. Sin el borrador |
| 11 | Datos de prueba | *Vestuario más destacado* y *Grupo de piloneras favorito* | Ejecuta el seeder otra vez | *Vestuario* abierta, *Grupo de piloneras favorito* próxima, 7 votaciones y 22 opciones |
| 12 | Pruebas automáticas | Terminal | `python manage.py test` | `Ran 43 tests` y `OK` |

## Casos CP-01 a CP-10

El **resultado obtenido**, el **estado** y el **minuto del video** los diligencia el equipo con lo que realmente salga en su ejecución.

| Caso | Procedimiento | Resultado esperado | Prueba automática |
|---|---|---|---|
| CP-01 | Con sesión iniciada, abrir *Canción favorita del público*, elegir una opción, **Continuar** y **Confirmar voto** | Mensaje «Tu voto por … quedó registrado» y una fila nueva en `elecciones_voto` | `test_cp01_*` |
| CP-02 | Abrir la misma votación en **dos pestañas**. Votar en la primera. En la segunda, elegir otra opción y **Continuar**. Después abrir *Agrupación favorita del público*, que es otro subevento de Música | La segunda pestaña muestra «Ya votaste en esta categoría»; el otro subevento no ofrece el formulario | `test_cp02_*` |
| CP-03 | Votar en *Vestuario más destacado* | Se registra: es otra categoría | `test_cp03_*` |
| CP-04 | Sin sesión, abrir una votación abierta y pulsar **Ingresar para votar**. Evidencia adicional: la prueba automática envía el POST sin sesión | Pide ingresar y no guarda nada. Sin token CSRF responde 403 | `test_cp04_*` |
| CP-05 | Abrir *Presentación más recordada* y *Grupo de piloneras favorito*: no ofrecen formulario. Evidencia del rechazo en el servidor: la prueba automática envía el POST | «Esta votación no está abierta». Un borrador o una categoría inactiva responden 404 | `test_cp05_*` |
| CP-06 | Con una cuenta que no haya votado en Música: en la página de la votación, con las herramientas del navegador (F12), cambiar el `value` de una opción por el id de una opción de otra categoría (se ve en `/api/categorias/`) y enviar | «La opción enviada no pertenece a esta votación» y no se guarda nada | `test_cp06_*` |
| CP-07 | Abrir **Mis votos** en el menú | Lista las categorías votadas, solo las de ese usuario | `test_cp07_*` |
| CP-08 | En `/admin`, abrir **Votos** y comparar con `SELECT * FROM elecciones_voto` en phpMyAdmin | Los datos coinciden. No hay opción de agregar, cambiar ni borrar | `test_cp08_*` |
| CP-09 | Ejecutar `python manage.py test apps.elecciones.tests.ConcurrenciaTests -v 2` y capturar la salida | Termina en `OK`: de 8 solicitudes simultáneas queda 1 voto y ninguna da error del servidor | `test_cp09_*` |
| CP-10 | Abrir `/api/categorias/` en el navegador o en Postman | JSON válido con categorías, votaciones y opciones reales | `test_cp10_*` |

## Guion del video

Un solo video por equipo, de **máximo 8 minutos**, con pantalla legible y audio claro. Lo puede presentar una sola persona, el delegado.

### Antes de grabar (el mismo día)

1. Pon el proyecto al día. Con MySQL encendido, dentro de `django/` y con el entorno activo:

```powershell
git checkout main
git pull
python manage.py migrate
python manage.py cargar_datos_prueba
python manage.py test
python manage.py runserver
```

   El seeder se corre el mismo día porque las fechas de las votaciones se calculan desde ese momento.

2. Crea **dos cuentas nuevas** en `/cuentas/registro/`, con nombres y correos ficticios (por ejemplo `votante1` y `votante2`). Un voto no se puede borrar: si algo sale mal, usa otra cuenta nueva.
3. Deja abiertas estas pestañas:
   - el sitio (`http://127.0.0.1:8000`);
   - phpMyAdmin (con **Apache** encendido en XAMPP) con las dos consultas de abajo, listas para ejecutar;
   - `/admin`, ya con sesión de superusuario en **otro navegador** o en una ventana de incógnito, para no cerrar la sesión del votante;
   - `/api/categorias/`.
4. En VS Code, deja abiertos estos archivos de `django/apps/elecciones/`: `models.py` (al final, el modelo `Voto`), `forms.py`, `views.py` (la vista `votar`) y `api.py`.
5. Pon el zoom del navegador en 125 % y agranda la letra de VS Code y de la terminal. Activa el modo *No molestar* de Windows y no muestres el archivo `.env`.
6. Para grabar sirve la **Herramienta Recortes** de Windows (`Windows + Shift + R`, opción de video) u **OBS Studio**, que es gratis. No uses la Xbox Game Bar, porque graba una sola ventana y en el video hay que cambiar entre el navegador, VS Code y phpMyAdmin.
7. Ten a mano un cronómetro o anota los minutos al ver el video: el PDF pide los **minutos reales** de cada parte.

### Paso a paso

| Minuto | Qué mostrar | Cómo | Casos |
|---|---|---|---|
| 0:00–0:45 | Presentación | Nombre del equipo, los cuatro integrantes, quién presenta y qué se implementó en esta entrega | — |
| 0:45–1:30 | Inicio de sesión y categorías | Entrar con `votante1`. Recorrer **Ediciones → 60.ª edición → Música**: los datos salen de MySQL | — |
| 1:30–2:30 | Voto válido | Abrir *Canción favorita del público* en **dos pestañas**. En la primera: elegir una opción, **Continuar a la confirmación**, **Confirmar voto**. Termina en **Mis votos** con el mensaje de éxito | CP-01 |
| 2:30–3:30 | Segundo voto en la misma categoría | En la segunda pestaña, elegir **otra** opción y continuar: sale el aviso rojo «Ya votaste en esta categoría». Luego abrir *Agrupación favorita del público*, otro subevento de Música: no ofrece formulario | CP-02 |
| 3:30–4:15 | Voto en otra categoría | Votar en *Vestuario más destacado* (Piloneras y vestuario): se registra | CP-03 |
| 4:15–5:00 | Historial y administración | **Mis votos** muestra las dos categorías. En `/admin` → **Votos** se ven los mismos datos, sin botón de agregar ni de borrar. En phpMyAdmin, la consulta de votos con nombres coincide | CP-07, CP-08 |
| 5:00–6:00 | API GET | Abrir `/api/categorias/`. Señalar la ruta, las categorías, sus votaciones y opciones, y que el borrador no aparece | CP-10 |
| 6:00–7:00 | MySQL y código | En phpMyAdmin, `SHOW CREATE TABLE elecciones_voto` y la línea `UNIQUE KEY`. En VS Code: `UniqueConstraint` en `models.py`, las validaciones en `forms.py`, el `try / except IntegrityError` en `views.py` y `api.py` | — |
| 7:00–8:00 | Pruebas adicionales y cierre | Salir de la cuenta y abrir una votación: pide **Ingresar para votar** (CP-04). Abrir *Presentación más recordada* (cerrada) y *Grupo de piloneras favorito* (próxima): no ofrecen formulario (CP-05). En la terminal, `python manage.py test apps.elecciones.tests.ConcurrenciaTests -v 2` termina en `OK` (CP-09). Cerrar con una conclusión corta | CP-04, CP-05, CP-09 |

**CP-06 (opción de otra categoría)** toma tiempo en vivo. Si cabe en el video, hazlo con `votante2` en *Canción favorita del público*:

1. Busca en `/api/categorias/` el `id` de una opción de otra categoría, por ejemplo *Vestuario A*.
2. Clic derecho sobre una opción → **Inspeccionar**.
3. En la línea `<input ... name="opcion" value="1">`, haz doble clic en el número y cámbialo por ese `id`.
4. Elige esa opción y pulsa **Continuar**: sale «La opción enviada no pertenece a esta votación».

Si no cabe, documéntalo en el PDF con capturas y con la salida de `python manage.py test apps.elecciones -v 2`, donde aparecen todas las pruebas `test_cp01` a `test_cp10` en `ok`. Lo mismo sirve para cualquier caso que no salga en el video.

### Después de grabar

1. Revisa que dure 8 minutos o menos y que se lea la pantalla.
2. Súbelo a YouTube como **No listado**.
3. Abre el enlace en una ventana de incógnito, sin sesión, y comprueba que se reproduce.
4. Pasa al equipo el enlace, la duración y los minutos reales de cada parte para el PDF.

## Consultas para mostrar MySQL en el video

En phpMyAdmin, pestaña SQL. Esta muestra la restricción; debe aparecer `UNIQUE KEY un_voto_por_usuario_categoria_edicion (usuario_id, edicion_id, categoria_id)`:

```sql
SHOW CREATE TABLE elecciones_voto;
```

Esta muestra los votos con nombres:

```sql
SELECT u.username, e.anio, c.nombre AS categoria, o.nombre AS opcion, v.fecha
FROM elecciones_voto v
JOIN auth_user u ON u.id = v.usuario_id
JOIN elecciones_edicion e ON e.id = v.edicion_id
JOIN elecciones_categoria c ON c.id = v.categoria_id
JOIN elecciones_opcion o ON o.id = v.opcion_id;
```

Durante la grabación, usa solo datos ficticios y no muestres el archivo `.env`.

## Datos para la ficha de acceso del PDF

| Elemento | Dato |
|---|---|
| Repositorio | https://github.com/sebastianbh/vallenata-festival-voting-system (rama `main`) |
| README | https://github.com/sebastianbh/vallenata-festival-voting-system/blob/main/django/README.md |
| API GET | `GET /api/categorias/`, en `django/apps/elecciones/api.py` |
| Control de duplicados | `django/apps/elecciones/models.py` (`UniqueConstraint`), `forms.py` (validación) y `views.py` (vista `votar`, `IntegrityError`) |

La API solo corre en `127.0.0.1`, así que en el PDF no se presenta como enlace remoto: se demuestra en el video y con una captura.

---

# Problemas comunes

| Si te pasa esto… | Haz esto |
|---|---|
| "python" no se reconoce como comando | Cierra VS Code por completo y ábrelo otra vez. Si sigue igual, ejecuta el instalador de Python, elige *Modify* y marca *Add Python to environment variables* |
| "La ejecución de scripts está deshabilitada" | Ejecuta una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a activar |
| `No module named 'django'` o `'environ'` | No activaste el entorno. Ejecuta `venv\Scripts\activate` y, si hace falta, `pip install -r requirements.txt` |
| `manage.py` no se encuentra | Estás en la carpeta equivocada. Entra con `cd django` |
| `Can't connect to server` (error 2002 o 2003) | MySQL está apagado. Dale **Start** en XAMPP |
| `Unknown database 'votaciones_festival'` | Falta crear la base. Repite el paso 1.5 |
| `Access denied for user 'root'` | Tu `root` tiene contraseña. Escríbela en `DB_PASSWORD` dentro de `.env` |
| `Set the SECRET_KEY environment variable` | Falta `.env` o su línea `SECRET_KEY`. Repite el paso 1.6. Debe estar al lado de `manage.py` |
| `You have N unapplied migration(s)` al encender el servidor | Faltan tablas. Detén el servidor y ejecuta `python manage.py migrate`: `runserver` no lo hace solo |
| `Table ... doesn't exist` | Igual que el anterior: ejecuta `python manage.py migrate` |
| El sitio abre, pero sin ediciones ni votaciones | La base está vacía. Ejecuta `python manage.py cargar_datos_prueba` |
| No hay votaciones abiertas | Las fechas ya pasaron. Ejecuta `python manage.py cargar_datos_prueba` |
| `Got an error creating the test database ... database exists` | Una ejecución de pruebas anterior se interrumpió. Responde `yes`: solo borra la base temporal |
| `'super' object has no attribute 'dicts'` en el admin (`change_list.html`) | Tienes Python 3.14 o más nuevo, y Django 4.2 solo funciona hasta la 3.13. Instala Python 3.13 y crea de nuevo el entorno: `deactivate`, borra la carpeta `venv`, y luego `py -3.13 -m venv venv`, `venv\Scripts\activate` y `pip install -r requirements.txt` |
| Olvidé la contraseña del superusuario | `python manage.py changepassword usuario` |
| `That port is already in use` | Ya hay un servidor encendido en otra terminal. Ciérralo con **Ctrl + C** o usa `python manage.py runserver 8001` |

### XAMPP: "MySQL shutdown unexpectedly"

**Qué pasa:** MySQL no enciende desde el panel de XAMPP y aparece este mensaje.

**Causa más común:** se apagó el computador o se cerró XAMPP sin detener MySQL primero. Eso puede dañar las tablas internas donde MySQL guarda los usuarios y permisos, y entonces se cierra apenas intenta leerlas.

**Cómo evitarlo:** antes de apagar el computador o cerrar XAMPP, presionar siempre **Stop** en MySQL.

**Cómo se arregló en este proyecto:** las tablas dañadas eran `db`, `proxies_priv` y `columns_priv` (en `C:\xampp\mysql\data\mysql\`). Con MySQL detenido, se guardó una copia de sus archivos y se reemplazaron por las originales que XAMPP trae en `C:\xampp\mysql\backup\mysql\`. Las bases de datos de los proyectos no se tocan, porque están en otras carpetas.

---

# Resumen de comandos

| Comando | Qué hace |
|---|---|
| `python --version` | Muestra la versión de Python instalada |
| `py -3.13 -m venv venv` | Crea el entorno virtual con Python 3.13 |
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
| `python manage.py changepassword usuario` | Cambia la contraseña de un usuario |
| `python manage.py test apps.elecciones -v 2` | Ejecuta las pruebas de una app y muestra cada una por su nombre |
| `git branch` | Muestra en qué rama estás (marcada con `*`) |
| `git checkout nombre-rama` | Cambia a otra rama |
| `git checkout -b nombre-rama` | Crea una rama nueva y se cambia a ella |
| `git pull` | Trae los cambios que subió el equipo a tu rama actual |
