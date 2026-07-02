# Paciente ve sus cuestionarios asignados
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

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

    # Set para lookup O(1) en template
    respondidos_ids = set(
        RespuestaCuestionario.objects.filter(
            paciente=request.user
        ).values_list('cuestionario_id', flat=True)
    )

    # Pendientes primero, luego ya respondidos
    asignaciones.sort(key=lambda a: a.cuestionario.pk in respondidos_ids)

    return render(request, 'cuestionarios/mis_cuestionarios_paciente.html', {
        'asignaciones': asignaciones,
        'respondidos_ids': respondidos_ids,
    })
