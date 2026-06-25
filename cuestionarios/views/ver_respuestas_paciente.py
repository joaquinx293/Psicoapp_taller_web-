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

    # Verificar que el paciente esté asignado a este especialista
    if not AsignacionCuestionario.objects.filter(
        especialista=request.user,
        paciente=paciente
    ).exists():
        return redirect('gestion_usuarios:listado_pacientes')

    # Todas las respuestas del paciente a cuestionarios de este especialista
    respuestas = RespuestaCuestionario.objects.filter(
        paciente=paciente,
        cuestionario__especialista=request.user,
    ).select_related('cuestionario').prefetch_related(
        'respuestas_preguntas__pregunta'
    ).order_by('-fecha_respuesta')

# --- LÓGICA HU-036: Preparar datos para el gráfico ---

    respuestas_grafico = respuestas.order_by('fecha_respuesta')
    
    evolucion = {}
    for r in respuestas_grafico:
        nombre_test = r.cuestionario.nombre
        if nombre_test not in evolucion:
            evolucion[nombre_test] = {'fechas': [], 'puntajes': []}
        
        fecha_exacta = r.fecha_respuesta.strftime('%d/%m/%Y %H:%M')
        evolucion[nombre_test]['fechas'].append(fecha_exacta)
        evolucion[nombre_test]['puntajes'].append(r.puntaje_total())

    evolucion_json = json.dumps(evolucion)

    return render(request, 'cuestionarios/ver_respuestas_paciente.html', {
        'paciente': paciente,
        'respuestas': respuestas,
        'evolucion_json': evolucion_json,
    })
