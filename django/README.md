# Sistema Web de Votaciones – Festival de la Leyenda Vallenata 2027

Proyecto académico en equipo del curso **Desarrollo Web** (Fundación Universitaria del Área Andina), **Entrega 2**: desarrollo inicial con **Python, Django (patrón MVT) y MySQL**.

El diseño reutiliza el prototipo HTML/CSS de la Entrega 1, que está en la raíz de este repositorio y se publica con GitHub Pages.

## Qué incluye esta entrega

- **Modelos relacionados**: Edición → Categoría → Votación → Opción, administrables desde Django Admin.
- **Autenticación** con el sistema estándar de Django: registro, inicio y cierre de sesión.
- **Interfaz pública** con datos reales de MySQL: inicio, ediciones, categorías de una edición, votaciones de una categoría y detalle de una votación con sus opciones.
- **Datos de prueba** ficticios que se cargan con un comando.
- **Pruebas automáticas** de modelos, vistas y cuentas.

El registro de votos y sus reglas corresponden a la siguiente entrega.

## Tecnologías

| Herramienta | Versión |
|---|---|
| Python | 3.13 |
| Django | 4.2 LTS |
| MySQL / MariaDB | MariaDB 10.4 (incluido en XAMPP 8.2) |
| mysqlclient | conector de MySQL para Django |
| django-environ | lectura de variables desde `.env` |
| Pillow | imágenes de las opciones |

> Se usa Django 4.2 porque las versiones 5.x exigen MariaDB 10.5 o superior, y XAMPP trae la 10.4.

## Estructura

```
django/
├── manage.py
├── requirements.txt
├── .env.example          plantilla de configuración (sin datos reales)
├── config/
│   ├── settings/
│   │   ├── base.py       configuración común
│   │   └── local.py      configuración de desarrollo
│   └── urls.py           rutas principales
├── apps/
│   ├── elecciones/       modelos, admin, vistas públicas y comando de datos de prueba
│   └── cuentas/          registro, inicio y cierre de sesión
├── templates/            base.html, parciales y una carpeta por app
├── static/               CSS, fuentes e imágenes del prototipo
└── docs/                 guías del equipo
```

## Instalación

Requisitos previos: **Python 3.13** (marcando *Add python.exe to PATH* al instalar), **XAMPP** y **Git**.

### 0. Clonar el repositorio

```powershell
git clone https://github.com/sebastianbh/vallenata-festival-voting-system.git votaciones-festival
cd votaciones-festival
```

Repositorio: https://github.com/sebastianbh/vallenata-festival-voting-system

A partir de aquí, todos los comandos se ejecutan en PowerShell, dentro de la carpeta `django/`.

### 1. Entorno virtual y dependencias

```powershell
cd django
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si PowerShell muestra *"la ejecución de scripts está deshabilitada"*, ejecutar una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y volver a activar.

### 2. Base de datos

1. Encender **MySQL** en el panel de XAMPP.
2. Crear la base en phpMyAdmin (http://localhost/phpmyadmin) o con este SQL:

```sql
CREATE DATABASE votaciones_festival CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Archivo `.env`

```powershell
copy .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Pegar la clave generada en `SECRET_KEY` dentro de `.env`. Con XAMPP los demás valores ya sirven (`root` sin contraseña, `127.0.0.1`, puerto `3306`). El archivo `.env` no se sube a GitHub.

### 4. Tablas, datos de prueba y superusuario

```powershell
python manage.py migrate
python manage.py cargar_datos_prueba
python manage.py createsuperuser
```

- `migrate` crea las tablas.
- `cargar_datos_prueba` carga 2 ediciones, 4 categorías, 6 votaciones (abiertas, próximas, cerradas y un borrador) y sus opciones. Todos los datos son ficticios. Se puede ejecutar de nuevo para refrescar las fechas sin duplicar registros.
- `createsuperuser` pide usuario, correo y contraseña para entrar al panel de administración.

## Ejecución

```powershell
python manage.py runserver
```

| Dirección | Qué hay |
|---|---|
| http://127.0.0.1:8000 | Sitio público |
| http://127.0.0.1:8000/admin | Panel de administración |
| http://127.0.0.1:8000/cuentas/registro/ | Crear cuenta |
| http://127.0.0.1:8000/cuentas/ingresar/ | Ingresar |

## Pruebas

```powershell
python manage.py test
```

Django crea una base de datos temporal para las pruebas y la borra al terminar.

## Documentación del equipo

- `docs/Guia-entorno-desarrollo.docx`: guía paso a paso para preparar el entorno en Windows.
- `docs/guia-paso-a-paso.md`: bitácora de cómo se construyó el proyecto, con los comandos explicados.

## Seguridad

- La clave secreta y las credenciales se leen del archivo `.env`, que está en `.gitignore`.
- El repositorio no contiene contraseñas ni datos reales; todos los datos de prueba son ficticios.
