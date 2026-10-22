"""Configuración del panel de administración (Django Admin) para los modelos del Festival."""

from django.contrib import admin
from django.db.models import Count

from .models import Categoria, Edicion, Opcion, Votacion

# Textos del encabezado del panel
admin.site.site_header = 'Administración · Votaciones Festival Vallenata'
admin.site.site_title = 'Votaciones Festival Vallenata'
admin.site.index_title = 'Panel de administración'


class CategoriaInline(admin.TabularInline):
    """Permite crear y editar categorías desde la pantalla de la edición."""

    model = Categoria
    fields = ['nombre', 'descripcion', 'activa']
    extra = 0


class OpcionInline(admin.TabularInline):
    """Permite agregar las opciones desde la misma pantalla de la votación."""

    model = Opcion
    fields = ['orden', 'nombre', 'descripcion', 'imagen']
    extra = 2


@admin.register(Edicion)
class EdicionAdmin(admin.ModelAdmin):
    list_display = ['numero', 'anio', 'nombre', 'lugar', 'fecha_inicio', 'fecha_fin', 'activa', 'en_portada']
    list_display_links = ['numero', 'anio']
    list_filter = ['activa', 'en_portada']
    search_fields = ['nombre', 'lugar']
    inlines = [CategoriaInline]


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'edicion', 'activa', 'total_votaciones']
    list_filter = ['edicion', 'activa']
    search_fields = ['nombre', 'descripcion']

    def get_queryset(self, request):
        # Cuenta las votaciones en la misma consulta para no hacer una consulta por fila
        return super().get_queryset(request).select_related('edicion').annotate(num_votaciones=Count('votaciones'))

    @admin.display(description='votaciones', ordering='num_votaciones')
    def total_votaciones(self, obj):
        return obj.num_votaciones


@admin.register(Votacion)
class VotacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'edicion', 'fecha_apertura', 'fecha_cierre', 'estado', 'publicada']
    list_filter = ['publicada', 'categoria__edicion', 'categoria']
    search_fields = ['titulo', 'descripcion']
    # Sin date_hierarchy: necesita las tablas de zonas horarias de MySQL, que XAMPP no trae instaladas
    list_select_related = ['categoria__edicion']
    inlines = [OpcionInline]

    @admin.display(description='edición', ordering='categoria__edicion__anio')
    def edicion(self, obj):
        return obj.categoria.edicion

    @admin.display(description='estado')
    def estado(self, obj):
        return obj.get_estado_display()


@admin.register(Opcion)
class OpcionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'votacion', 'orden']
    list_filter = ['votacion__categoria__edicion', 'votacion']
    search_fields = ['nombre', 'descripcion']
    list_select_related = ['votacion']
