# Paciente ve sus cuestionarios asignados
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from ..models import AsignacionCuestionario, RespuestaCuestionario


@login_required
def mis_cuestionarios_paciente(request):
    if not request.user.es_paciente():
        return redirect('cuentas:login')

    asignaciones = list(
        AsignacionCuestionario.objects.filter(
            paciente=request.user,
            activa=True
        ).select_related('cuestionario').order_by('cuestionario__nombre')
    )

    # Intentos usados por cuestionario: {cuestionario_id: count}
    intentos_usados = {
        r['cuestionario_id']: r['total']
        for r in RespuestaCuestionario.objects.filter(
            paciente=request.user
        ).values('cuestionario_id').annotate(total=Count('id'))
    }

    # Set para detectar "al menos una respuesta" (para badge de estado)
    respondidos_ids = set(intentos_usados.keys())

    # Construir lista enriquecida para el template
    items = []
    for asig in asignaciones:
        cid = asig.cuestionario_id
        usados = intentos_usados.get(cid, 0)
        max_i  = asig.intentos_maximos  # 0 = ilimitado
        if max_i == 0:
            agotado   = False
            restantes = None  # ilimitado
        else:
            agotado   = usados >= max_i
            restantes = max(0, max_i - usados)

        items.append({
            'asignacion': asig,
            'cuestionario': asig.cuestionario,
            'respondido': cid in respondidos_ids,
            'intentos_usados': usados,
            'intentos_maximos': max_i,
            'restantes': restantes,
            'agotado': agotado,
        })

    # Pendientes/disponibles primero, luego agotados
    items.sort(key=lambda x: (x['agotado'], x['respondido']))

    return render(request, 'cuestionarios/mis_cuestionarios_paciente.html', {
        'items':         items,
        # Mantener compatibilidad con badge en perfil_paciente (login.py ya lo calcula)
        'respondidos_ids': respondidos_ids,
    })
