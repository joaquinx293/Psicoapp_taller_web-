# Paciente responde un cuestionario
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import (
    Cuestionario, AsignacionCuestionario,
    RespuestaCuestionario, RespuestaPregunta
)

OPCIONES_ESCALA = {
    'likert4': [(0, 'Nunca'), (1, 'Raramente'), (2, 'A veces'), (3, 'Siempre')],
    'likert5': [(0, 'Nunca'), (1, 'Casi nunca'), (2, 'A veces'), (3, 'Frecuentemente'), (4, 'Casi siempre')],
    'sino':    [(1, 'Sí'), (0, 'No')],
    'gad7':   [(0, 'Nunca'), (1, 'Varios días'), (2, 'La mitad de los días'), (3, 'Casi cada día')],
}


@login_required
def responder_cuestionario(request, pk):
    if not request.user.es_paciente():
        return redirect('cuentas:login')

    cuestionario = get_object_or_404(Cuestionario, pk=pk)

    # Verificar que esté asignado a este paciente
    if not AsignacionCuestionario.objects.filter(
        paciente=request.user,
        cuestionario=cuestionario,
        activa=True
    ).exists():
        messages.error(request, 'Este cuestionario no está disponible para ti.')
        return redirect('cuestionarios:mis_cuestionarios_paciente')

    preguntas = cuestionario.preguntas.filter(activa=True)

    if request.method == 'POST':
        respuestas_validas = {}
        error = False

        for pregunta in preguntas:
            key = f'pregunta_{pregunta.pk}'
            valor = request.POST.get(key)
            if valor is None:
                messages.error(request, f'Debes responder todas las preguntas.')
                error = True
                break
            respuestas_validas[pregunta.pk] = int(valor)

        if not error:
            respuesta = RespuestaCuestionario.objects.create(
                paciente=request.user,
                cuestionario=cuestionario,
            )
            for pregunta in preguntas:
                RespuestaPregunta.objects.create(
                    respuesta_cuestionario=respuesta,
                    pregunta=pregunta,
                    valor=respuestas_validas[pregunta.pk],
                )
            return redirect('cuestionarios:resultado_cuestionario', respuesta_pk=respuesta.pk)

    # Preparar preguntas con sus opciones de respuesta
    preguntas_con_opciones = [
        (p, OPCIONES_ESCALA.get(p.escala, OPCIONES_ESCALA['likert4']))
        for p in preguntas
    ]

    return render(request, 'cuestionarios/responder_cuestionario.html', {
        'cuestionario': cuestionario,
        'preguntas_con_opciones': preguntas_con_opciones,
    })
