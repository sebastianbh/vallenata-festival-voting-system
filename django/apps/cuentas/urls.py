from django.urls import path

from . import views

app_name = 'cuentas'

urlpatterns = [
    path('ingresar/', views.IngresoView.as_view(), name='ingresar'),
    path('salir/', views.SalidaView.as_view(), name='salir'),
    path('registro/', views.registro, name='registro'),
]
