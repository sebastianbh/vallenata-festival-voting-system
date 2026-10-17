"""
Configuración común a todos los entornos (desarrollo, pruebas, producción).

Los datos privados (clave secreta, credenciales de la base de datos) no se
escriben aquí: se leen del archivo .env, que no se sube a Git.
"""

from pathlib import Path

import environ

# Carpeta raíz del proyecto Django (la que contiene manage.py).
# Este archivo está en config/settings/, por eso se sube tres niveles.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Lee las variables del archivo .env ubicado junto a manage.py.
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')


# Aplicaciones instaladas

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps del proyecto
    'apps.elecciones',
    'apps.cuentas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Plantillas del proyecto (base.html, parciales y una carpeta por app).
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Base de datos: MySQL/MariaDB de XAMPP, con los datos tomados del .env

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default='127.0.0.1'),
        'PORT': env('DB_PORT', default='3306'),
        'OPTIONS': {
            # utf8mb4 guarda cualquier carácter: tildes, ñ y emojis.
            'charset': 'utf8mb4',
            # Modo estricto: MySQL rechaza datos inválidos en vez de recortarlos en silencio.
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# Validación de contraseñas al registrarse

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Autenticación: a dónde llevar al usuario al ingresar o salir

LOGIN_URL = 'cuentas:ingresar'
LOGIN_REDIRECT_URL = 'elecciones:inicio'
LOGOUT_REDIRECT_URL = 'elecciones:inicio'


# Idioma y zona horaria de Colombia

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True


# Archivos estáticos (CSS, JavaScript, imágenes del diseño)

STATIC_URL = 'static/'
# CSS, fuentes e imágenes copiados del prototipo
STATICFILES_DIRS = [BASE_DIR / 'static']

# Archivos subidos desde el panel (imágenes de las opciones). No se suben a Git.
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Tipo de llave primaria por defecto para los modelos
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
