"""
Configuración para desarrollo en el computador de cada integrante.

Hereda todo lo de base.py y solo cambia lo propio del entorno local.
"""

from .base import *  # noqa: F401,F403

# Muestra las páginas de error detalladas. Nunca activarlo en un servidor real.
DEBUG = env.bool('DEBUG', default=True)

# Direcciones desde las que se puede abrir el sitio en desarrollo.
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
