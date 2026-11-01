from django.urls import path

from . import api, views

# Permite referirse a las rutas como 'elecciones:inicio', 'elecciones:detalle_votacion', etc.
app_name = 'elecciones'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('ediciones/', views.lista_ediciones, name='lista_ediciones'),
    path('ediciones/<int:pk>/', views.detalle_edicion, name='detalle_edicion'),
    path('categorias/<int:pk>/', views.detalle_categoria, name='detalle_categoria'),
    path('votaciones/<int:pk>/', views.detalle_votacion, name='detalle_votacion'),
    path('votaciones/<int:pk>/votar/', views.votar, name='votar'),
    path('mis-votos/', views.mis_votos, name='mis_votos'),
    path('api/categorias/', api.categorias, name='api_categorias'),
]
