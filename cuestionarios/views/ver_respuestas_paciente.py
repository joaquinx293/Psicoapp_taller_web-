import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from ..models import RespuestaCuestionario, AsignacionCuestionario

Usuario = get_user_model()


@login_required
def ver_respuestas_paciente(request, paciente_pk):
    """El especialista ve el historial de respuestas de uno de sus pacientes."""
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    paciente = get_object_or_404(Usuario, pk=paciente_pk, rol='paciente')

    if not AsignacionCuestionario.objects.filter(
        especialista=request.user,
        paciente=paciente
    ).exists():
        return redirect('gestion_usuarios:listado_pacientes')

    respuestas = RespuestaCuestionario.objects.filter(
        paciente=paciente,
        cuestionario__especialista=request.user,
    ).select_related('cuestionario').prefetch_related(
        'respuestas_preguntas__pregunta'
    ).order_by('-fecha_respuesta')

    # HU-036: datos para gráfico de evolución de puntajes
    evolucion = {}
    for r in respuestas.order_by('fecha_respuesta'):
        nombre_test = r.cuestionario.nombre
        if nombre_test not in evolucion:
            evolucion[nombre_test] = {'fechas': [], 'puntajes': []}
        evolucion[nombre_test]['fechas'].append(r.fecha_respuesta.strftime('%d/%m/%Y %H:%M'))
        evolucion[nombre_test]['puntajes'].append(r.puntaje_total())

    return render(request, 'cuestionarios/ver_respuestas_paciente.html', {
        'paciente': paciente,
        'respuestas': respuestas,
        'evolucion_json': json.dumps(evolucion),
    })
