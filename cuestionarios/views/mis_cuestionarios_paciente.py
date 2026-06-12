# Paciente ve sus cuestionarios asignados
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from ..models import AsignacionCuestionario, RespuestaCuestionario


@login_required
def mis_cuestionarios_paciente(request):
    if not request.user.es_paciente():
        return redirect('cuentas:login')

    asignaciones = AsignacionCuestionario.objects.filter(
        paciente=request.user,
        activa=True
    ).select_related('cuestionario')

    # Cuestionarios ya respondidos por este paciente
    respondidos_ids = RespuestaCuestionario.objects.filter(
        paciente=request.user
    ).values_list('cuestionario_id', flat=True)

    return render(request, 'cuestionarios/mis_cuestionarios_paciente.html', {
        'asignaciones': asignaciones,
        'respondidos_ids': list(respondidos_ids),
    })
