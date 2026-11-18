"""Configuración del panel de administración (Django Admin) para los modelos del Festival."""

from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from .models import Categoria, Edicion, Opcion, Votacion, Voto

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
    fields = ['orden', 'nombre', 'descripcion', 'imagen', 'votos_recibidos']
    readonly_fields = ['votos_recibidos']
    extra = 2

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(num_votos=Count('votos'))

    @admin.display(description='votos')
    def votos_recibidos(self, obj):
        # Las filas nuevas (todavía sin guardar) no tienen votos
        return getattr(obj, 'num_votos', 0)


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
    list_display = ['titulo', 'categoria', 'edicion', 'fecha_apertura', 'fecha_cierre', 'estado', 'publicada', 'resultados', 'total_votos']
    list_filter = ['publicada', 'resultados', 'categoria__edicion', 'categoria']
    search_fields = ['titulo', 'descripcion']
    # Sin date_hierarchy: necesita las tablas de zonas horarias de MySQL, que XAMPP no trae instaladas
    list_select_related = ['categoria__edicion']
    readonly_fields = ['enlace_resultados']
    inlines = [OpcionInline]

    def get_queryset(self, request):
        # Cuenta los votos de todas sus opciones en la misma consulta
        return super().get_queryset(request).annotate(num_votos=Count('opciones__votos'))

    @admin.display(description='votos', ordering='num_votos')
    def total_votos(self, obj):
        return obj.num_votos

    @admin.display(description='resultados en el sitio')
    def enlace_resultados(self, obj):
        if not obj.pk:
            return 'Disponible después de guardar.'
        url = reverse('elecciones:resultados_votacion', args=[obj.pk])
        return format_html('<a href="{}" target="_blank" rel="noopener">Ver la página de resultados</a>', url)

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


@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    """Los votos solo se consultan: nadie puede crearlos, cambiarlos ni borrarlos desde el panel."""

    list_display = ['fecha', 'usuario', 'edicion', 'categoria', 'opcion']
    list_filter = ['edicion', 'categoria']
    search_fields = ['usuario__username', 'opcion__nombre']
    list_select_related = ['usuario', 'edicion', 'categoria', 'opcion']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
