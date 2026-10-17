from django.urls import path

from . import views

# Permite referirse a las rutas como 'elecciones:inicio', 'elecciones:detalle_votacion', etc.
app_name = 'elecciones'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('ediciones/', views.lista_ediciones, name='lista_ediciones'),
    path('ediciones/<int:pk>/', views.detalle_edicion, name='detalle_edicion'),
    path('categorias/<int:pk>/', views.detalle_categoria, name='detalle_categoria'),
    path('votaciones/<int:pk>/', views.detalle_votacion, name='detalle_votacion'),
]
