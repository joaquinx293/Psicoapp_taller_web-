# HU-019/HU-018: Resultado del cuestionario tras responderlo (GAD-7, PSS-10, PHQ-9)
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from ..models import Cuestionario, RespuestaCuestionario


@login_required
def resultado_cuestionario(request, respuesta_pk):
    if not request.user.es_paciente():
        return render(request, 'cuestionarios/resultado_cuestionario.html', {})

    respuesta = get_object_or_404(
        RespuestaCuestionario,
        pk=respuesta_pk,
        paciente=request.user,
    )

    subtipo = respuesta.cuestionario.subtipo
    es_gad7  = subtipo == Cuestionario.SUBTIPO_GAD7
    es_pss10 = subtipo == Cuestionario.SUBTIPO_PSS10
    es_phq9  = subtipo == Cuestionario.SUBTIPO_PHQ9

    if es_gad7:
        clasificacion = respuesta.clasificacion_gad7()
    elif es_pss10:
        clasificacion = respuesta.clasificacion_pss10()
    elif es_phq9:
        clasificacion = respuesta.clasificacion_phq9()
    else:
        clasificacion = None

    return render(request, 'cuestionarios/resultado_cuestionario.html', {
        'respuesta':    respuesta,
        'puntaje':      respuesta.puntaje_total(),
        'es_gad7':      es_gad7,
        'es_pss10':     es_pss10,
        'es_phq9':      es_phq9,
        'clasificacion': clasificacion,
    })
