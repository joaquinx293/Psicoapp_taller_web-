# Paciente responde un cuestionario
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import (
    Cuestionario, Pregunta, AsignacionCuestionario,
    RespuestaCuestionario, RespuestaPregunta
)

OPCIONES_ESCALA = {
    'likert4': [(0, 'Nunca'), (1, 'Raramente'), (2, 'A veces'), (3, 'Siempre')],
    'likert5': [(0, 'Nunca'), (1, 'Casi nunca'), (2, 'A veces'), (3, 'Frecuentemente'), (4, 'Casi siempre')],
    'sino':    [(1, 'Sí'), (0, 'No')],
    'gad7':    [(0, 'Nunca'), (1, 'Varios días'), (2, 'La mitad de los días'), (3, 'Casi cada día')],
    'pss10':   [(0, 'Nunca'), (1, 'Casi nunca'), (2, 'De vez en cuando'), (3, 'A menudo'), (4, 'Muy a menudo')],
    'phq9':    [(0, 'Ningún día'), (1, 'Varios días'), (2, 'Más de la mitad de los días'), (3, 'Casi todos los días')],
    'verdadero_falso': [(1, 'Verdadero'), (0, 'Falso')],
}


@login_required
def responder_cuestionario(request, pk):
    if not request.user.es_paciente():
        return redirect('cuentas:login')

    cuestionario = get_object_or_404(Cuestionario, pk=pk)

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

            if pregunta.escala in Pregunta.ESCALAS_VALOR_TEXTO:
                valor_txt = request.POST.get(key, '').strip()
                if not valor_txt:
                    messages.error(request, 'Debes completar todas las preguntas.')
                    error = True
                    break
                respuestas_validas[pregunta.pk] = {'texto': valor_txt}
            else:
                valor = request.POST.get(key)
                if valor is None:
                    messages.error(request, 'Debes responder todas las preguntas.')
                    error = True
                    break
                respuestas_validas[pregunta.pk] = {'valor': int(valor)}

        if not error:
            respuesta = RespuestaCuestionario.objects.create(
                paciente=request.user,
                cuestionario=cuestionario,
            )
            for pregunta in preguntas:
                data = respuestas_validas[pregunta.pk]
                if 'texto' in data:
                    RespuestaPregunta.objects.create(
                        respuesta_cuestionario=respuesta,
                        pregunta=pregunta,
                        valor=None,
                        valor_texto=data['texto'],
                    )
                else:
                    RespuestaPregunta.objects.create(
                        respuesta_cuestionario=respuesta,
                        pregunta=pregunta,
                        valor=data['valor'],
                    )
            return redirect('cuestionarios:resultado_cuestionario', respuesta_pk=respuesta.pk)

    # Preparar preguntas con sus opciones
    preguntas_con_opciones = []
    for p in preguntas:
        if p.escala == Pregunta.ESCALA_BINARIO:
            opciones = [
                (0, p.etiqueta_opcion_1 or 'Opcion 1'),
                (1, p.etiqueta_opcion_2 or 'Opcion 2'),
            ]
        else:
            opciones = OPCIONES_ESCALA.get(p.escala, [])
        preguntas_con_opciones.append((p, opciones))

    return render(request, 'cuestionarios/responder_cuestionario.html', {
        'cuestionario': cuestionario,
        'preguntas_con_opciones': preguntas_con_opciones,
    })
