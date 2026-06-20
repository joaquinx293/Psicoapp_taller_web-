# HU: Reordenar preguntas de un cuestionario personalizado
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..models import Cuestionario, Pregunta


@login_required
def reordenar_preguntas(request, pk):
    """Vista para reorganizar el orden de las preguntas via drag & drop."""
    cuestionario = get_object_or_404(
        Cuestionario,
        pk=pk,
        especialista=request.user,
        subtipo=Cuestionario.SUBTIPO_PERSONALIZADO,
    )

    # Solo cuestionarios en borrador o rechazado son editables
    if cuestionario.estado not in (Cuestionario.BORRADOR, Cuestionario.RECHAZADO):
        return redirect('cuestionarios:detalle', pk=pk)

    if not request.user.es_especialista():
        return redirect('cuentas:login')

    preguntas = cuestionario.preguntas.filter(activa=True)

    return render(request, 'cuestionarios/reordenar_preguntas.html', {
        'cuestionario': cuestionario,
        'preguntas': preguntas,
    })


@login_required
@require_POST
def guardar_orden(request, pk):
    """Endpoint AJAX: recibe lista de IDs ordenados y actualiza el campo orden."""
    cuestionario = get_object_or_404(
        Cuestionario,
        pk=pk,
        especialista=request.user,
        subtipo=Cuestionario.SUBTIPO_PERSONALIZADO,
    )

    if cuestionario.estado not in (Cuestionario.BORRADOR, Cuestionario.RECHAZADO):
        return JsonResponse({'ok': False, 'error': 'Cuestionario no editable.'}, status=403)

    try:
        datos = json.loads(request.body)
        ids_ordenados = datos.get('orden', [])
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'ok': False, 'error': 'JSON inválido.'}, status=400)

    # Verificar que todos los IDs pertenecen a este cuestionario
    ids_validos = set(
        cuestionario.preguntas.filter(activa=True).values_list('id', flat=True)
    )
    if not all(pid in ids_validos for pid in ids_ordenados):
        return JsonResponse({'ok': False, 'error': 'IDs inválidos.'}, status=400)

    for posicion, pregunta_id in enumerate(ids_ordenados, start=1):
        Pregunta.objects.filter(pk=pregunta_id).update(orden=posicion)

    return JsonResponse({'ok': True})
