"""API de solo lectura: entrega en JSON la información guardada en MySQL."""

from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Categoria, Votacion


def opcion_a_dict(opcion):
    return {
        'id': opcion.pk,
        'nombre': opcion.nombre,
        'descripcion': opcion.descripcion,
        'imagen': opcion.imagen.url if opcion.imagen else None,
    }


def votacion_a_dict(votacion):
    return {
        'id': votacion.pk,
        'titulo': votacion.titulo,
        'estado': votacion.estado,
        'fecha_apertura': votacion.fecha_apertura.isoformat(),
        'fecha_cierre': votacion.fecha_cierre.isoformat(),
        'opciones': [opcion_a_dict(opcion) for opcion in votacion.opciones.all()],
    }


def categoria_a_dict(categoria):
    edicion = categoria.edicion
    return {
        'id': categoria.pk,
        'nombre': categoria.nombre,
        'descripcion': categoria.descripcion,
        'edicion': {'id': edicion.pk, 'numero': edicion.numero, 'anio': edicion.anio, 'nombre': edicion.nombre},
        'votaciones': [votacion_a_dict(votacion) for votacion in categoria.votaciones.all()],
    }


@require_GET
def categorias(request):
    """GET /api/categorias/: categorías visibles con sus votaciones y opciones."""
    # prefetch_related trae todo en pocas consultas, en vez de hacer una por cada fila.
    # Los borradores se excluyen, igual que en las páginas públicas.
    publicadas = Votacion.objects.filter(publicada=True).prefetch_related('opciones')
    consulta = (
        Categoria.objects
        .filter(activa=True, edicion__activa=True)
        .select_related('edicion')
        .prefetch_related(Prefetch('votaciones', queryset=publicadas))
    )
    datos = [categoria_a_dict(categoria) for categoria in consulta]
    # ensure_ascii=False conserva las tildes; indent hace legible el JSON en el navegador
    return JsonResponse({'total': len(datos), 'categorias': datos}, json_dumps_params={'ensure_ascii': False, 'indent': 2})
