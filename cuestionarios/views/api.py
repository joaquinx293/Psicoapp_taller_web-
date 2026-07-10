# Endpoints AJAX para búsqueda escalable de preguntas y cuestionarios
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from ..models import Cuestionario, Pregunta, AsignacionCuestionario


@login_required
def buscar_pregunta(request, cuestionario_pk):
    """
    GET /cuestionarios/api/buscar-pregunta/<pk>/?q=texto
    Devuelve hasta 20 preguntas de otros cuestionarios del especialista,
    deduplicadas por texto exacto (case-insensitive).
    """
    if not request.user.es_especialista():
        return JsonResponse({'error': 'No autorizado'}, status=403)

    q = request.GET.get('q', '').strip()

    qs = Pregunta.objects.filter(
        cuestionario__especialista=request.user,
        activa=True,
    ).exclude(
        cuestionario_id=cuestionario_pk,
    ).select_related('cuestionario').order_by('cuestionario__nombre', 'orden')

    if q:
        qs = qs.filter(
            Q(texto__icontains=q) | Q(cuestionario__nombre__icontains=q)
        )

    # Deduplicar en Python (mismo texto → una sola entrada); cap en 200 filas de BD
    seen = set()
    results = []
    for p in qs[:200]:
        key = p.texto.lower().strip()
        if key not in seen:
            seen.add(key)
            results.append({
                'id': p.pk,
                'texto': p.texto,
                'cuestionario': p.cuestionario.nombre,
            })
        if len(results) >= 20:
            break

    return JsonResponse({'results': results})


@login_required
def buscar_cuestionario(request):
    """
    GET /cuestionarios/api/buscar-cuestionario/?q=texto
    Devuelve hasta 20 cuestionarios disponibles para asignar a un paciente.
    Misma lógica de elegibilidad que asignar_cuestionario.py.
    """
    if not request.user.es_especialista():
        return JsonResponse({'error': 'No autorizado'}, status=403)

    q = request.GET.get('q', '').strip()

    qs = (
        Cuestionario.objects.filter(
            estado__in=[Cuestionario.APROBADO, Cuestionario.PUBLICADO],
        ) | Cuestionario.objects.filter(
            especialista=request.user,
            estado__in=[Cuestionario.BORRADOR, Cuestionario.APROBADO, Cuestionario.PUBLICADO],
        )
    ).distinct()

    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))

    qs = qs.order_by('nombre')

    results = []
    for c in qs[:20]:
        results.append({
            'id': c.pk,
            'nombre': c.nombre,
            'descripcion': (c.descripcion or '')[:80],
            'estado': c.estado,
            'estado_display': c.get_estado_display(),
            'n_preguntas': c.cantidad_preguntas_activas(),
        })

    return JsonResponse({'results': results})
