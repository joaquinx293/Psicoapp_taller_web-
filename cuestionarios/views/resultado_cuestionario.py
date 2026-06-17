# HU-019: Resultado del cuestionario tras responderlo (con clasificación GAD-7)
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from ..models import RespuestaCuestionario


@login_required
def resultado_cuestionario(request, respuesta_pk):
    if not request.user.es_paciente():
        return render(request, 'cuestionarios/resultado_cuestionario.html', {})

    respuesta = get_object_or_404(
        RespuestaCuestionario,
        pk=respuesta_pk,
        paciente=request.user,
    )

    es_gad7 = respuesta.cuestionario.subtipo == 'gad7'
    clasificacion = respuesta.clasificacion_gad7() if es_gad7 else None

    return render(request, 'cuestionarios/resultado_cuestionario.html', {
        'respuesta': respuesta,
        'puntaje': respuesta.puntaje_total(),
        'es_gad7': es_gad7,
        'clasificacion': clasificacion,
    })
