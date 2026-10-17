from django.apps import AppConfig


class EleccionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Ruta completa porque la app está dentro de la carpeta apps/
    name = 'apps.elecciones'
    # Nombre que se muestra en el panel de administración
    verbose_name = 'Elecciones del Festival'
