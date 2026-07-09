from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from cuentas.models import Usuario
from ..models import AsignacionCuestionario, RespuestaCuestionario

@login_required
def ver_adherencia_paciente(request, paciente_pk):
    """Calcula el porcentaje de cuestionarios completados por un paciente."""
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    paciente = get_object_or_404(Usuario, pk=paciente_pk, rol=Usuario.ROL_PACIENTE)
    
    # Obtener todas las asignaciones activas
    asignaciones = AsignacionCuestionario.objects.filter(paciente=paciente, activa=True)
    
    # Obtener IDs de cuestionarios respondidos por el paciente
    respondidos_ids = RespuestaCuestionario.objects.filter(
        paciente=paciente
    ).values_list('cuestionario_id', flat=True).distinct()

    datos_adherencia = []
    for asig in asignaciones:
        respondido = asig.cuestionario_id in respondidos_ids
        datos_adherencia.append({
            'nombre': asig.cuestionario.nombre,
            'completado': respondido
        })

    total = asignaciones.count()
    completados = len([d for d in datos_adherencia if d['completado']])
    tasa = (completados / total * 100) if total > 0 else 0

    return render(request, 'cuestionarios/adherencia_paciente.html', {
        'paciente': paciente,
        'datos': datos_adherencia,
        'tasa': round(tasa, 1),
        'total': total,
        'completados': completados
    })
