"""
Rutas principales del proyecto.

Cada app tiene su propio urls.py y aquí se incluye con include().
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/', include('apps.cuentas.urls')),
    path('', include('apps.elecciones.urls')),
]

# En desarrollo, el servidor de Django también entrega las imágenes subidas (carpeta media/)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
