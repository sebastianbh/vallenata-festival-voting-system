"""
Vistas públicas: leen los datos de MySQL y se los pasan a las plantillas.

Solo se muestra lo que la administración dejó visible:
ediciones y categorías activas, y votaciones publicadas.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import VotoForm
from .models import Categoria, Edicion, Votacion, Voto


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
    # La edición que la administración marcó para la portada (o la más reciente)
    edicion = Edicion.de_portada()
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
    voto = Voto.de_usuario(request.user, categoria) if request.user.is_authenticated else None
    contexto = {
        'votacion': votacion,
        'opciones': votacion.opciones.all(),
        'voto': voto,
        'puede_votar': request.user.is_authenticated and votacion.estado == Votacion.ABIERTA and not voto,
        'migas': migas_hasta(miga_edicion(categoria.edicion), miga_categoria(categoria), (votacion.titulo, None)),
    }
    return render(request, 'elecciones/votacion_detalle.html', contexto)


@login_required
def votar(request, pk):
    """Recibe la opción elegida, pide confirmarla y, una vez confirmada, guarda el voto."""
    votacion = get_object_or_404(votaciones_visibles(), pk=pk)
    # Se llega aquí sin POST cuando alguien inicia sesión después de intentar votar
    if request.method != 'POST':
        return redirect('elecciones:detalle_votacion', pk=pk)

    form = VotoForm(request.POST, votacion=votacion, usuario=request.user)
    if not form.is_valid():
        for errores in form.errors.values():
            for error in errores:
                messages.error(request, error)
        return redirect('elecciones:detalle_votacion', pk=pk)

    opcion = form.cleaned_data['opcion']
    if 'confirmado' not in request.POST:
        categoria = votacion.categoria
        contexto = {
            'votacion': votacion,
            'opcion': opcion,
            'migas': migas_hasta(
                miga_edicion(categoria.edicion), miga_categoria(categoria),
                (votacion.titulo, reverse('elecciones:detalle_votacion', args=[pk])), ('Confirmar voto', None),
            ),
        }
        return render(request, 'elecciones/voto_confirmar.html', contexto)

    # Dos solicitudes simultáneas pueden pasar juntas la validación del formulario.
    # En ese caso MySQL guarda solo una y a la otra le responde con un IntegrityError.
    try:
        with transaction.atomic():
            Voto.registrar(request.user, opcion)
    except IntegrityError:
        messages.error(request, 'Ya votaste en esta categoría: solo se permite un voto por categoría y edición.')
        return redirect('elecciones:detalle_votacion', pk=pk)

    messages.success(request, f'Tu voto por {opcion.nombre} quedó registrado.')
    return redirect('elecciones:mis_votos')


@login_required
def mis_votos(request):
    votos = request.user.votos.select_related('edicion', 'categoria', 'opcion__votacion')
    contexto = {
        'votos': votos,
        'migas': [('Inicio', reverse('elecciones:inicio')), ('Mis votos', None)],
    }
    return render(request, 'elecciones/mis_votos.html', contexto)
