"""
Vistas públicas: leen los datos de MySQL y se los pasan a las plantillas.

Solo se muestra lo que la administración dejó visible:
ediciones y categorías activas, y votaciones publicadas.
"""

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone

from .models import Categoria, Edicion, Votacion


def migas_hasta(*pasos):
    """Ruta de navegación (migas de pan) que empieza en Inicio > Ediciones."""
    return [('Inicio', reverse('elecciones:inicio')), ('Ediciones', reverse('elecciones:lista_ediciones')), *pasos]


def miga_edicion(edicion):
    return (f'{edicion.numero}.ª edición', reverse('elecciones:detalle_edicion', args=[edicion.pk]))


def miga_categoria(categoria):
    return (categoria.nombre, reverse('elecciones:detalle_categoria', args=[categoria.pk]))


def votaciones_visibles():
    """Votaciones publicadas cuya categoría y edición están activas."""
    return (
        Votacion.objects
        .filter(publicada=True, categoria__activa=True, categoria__edicion__activa=True)
        .select_related('categoria__edicion')
        .annotate(num_opciones=Count('opciones'))
    )


def categorias_con_conteos(edicion):
    """Categorías activas de una edición, con cuántas votaciones tiene cada una y cuántas están abiertas."""
    ahora = timezone.now()
    publicadas = Q(votaciones__publicada=True)
    abiertas = publicadas & Q(votaciones__fecha_apertura__lte=ahora, votaciones__fecha_cierre__gt=ahora)
    return edicion.categorias.filter(activa=True).annotate(
        num_votaciones=Count('votaciones', filter=publicadas),
        num_abiertas=Count('votaciones', filter=abiertas),
    )


def inicio(request):
    ahora = timezone.now()
    # La edición más reciente que esté activa (el modelo ordena por año descendente)
    edicion = Edicion.objects.filter(activa=True).first()
    abiertas = votaciones_visibles().filter(fecha_apertura__lte=ahora, fecha_cierre__gt=ahora)
    contexto = {
        'edicion': edicion,
        'votaciones_abiertas': abiertas,
        'categorias': categorias_con_conteos(edicion) if edicion else [],
    }
    return render(request, 'elecciones/inicio.html', contexto)


def lista_ediciones(request):
    ediciones = Edicion.objects.filter(activa=True).annotate(
        num_categorias=Count('categorias', filter=Q(categorias__activa=True)),
    )
    contexto = {'ediciones': ediciones, 'migas': migas_hasta()}
    return render(request, 'elecciones/ediciones.html', contexto)


def detalle_edicion(request, pk):
    edicion = get_object_or_404(Edicion, pk=pk, activa=True)
    contexto = {
        'edicion': edicion,
        'categorias': categorias_con_conteos(edicion),
        'migas': migas_hasta(miga_edicion(edicion)),
    }
    return render(request, 'elecciones/edicion_detalle.html', contexto)


def detalle_categoria(request, pk):
    categoria = get_object_or_404(
        Categoria.objects.select_related('edicion'), pk=pk, activa=True, edicion__activa=True,
    )
    contexto = {
        'categoria': categoria,
        'votaciones': votaciones_visibles().filter(categoria=categoria),
        'migas': migas_hasta(miga_edicion(categoria.edicion), miga_categoria(categoria)),
    }
    return render(request, 'elecciones/categoria_detalle.html', contexto)


def detalle_votacion(request, pk):
    votacion = get_object_or_404(votaciones_visibles(), pk=pk)
    categoria = votacion.categoria
    contexto = {
        'votacion': votacion,
        'opciones': votacion.opciones.all(),
        'migas': migas_hasta(miga_edicion(categoria.edicion), miga_categoria(categoria), (votacion.titulo, None)),
    }
    return render(request, 'elecciones/votacion_detalle.html', contexto)
