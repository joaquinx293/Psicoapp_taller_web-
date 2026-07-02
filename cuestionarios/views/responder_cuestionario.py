# Paciente responde un cuestionario (con paginación de 5 preguntas por página)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import (
    Cuestionario, Pregunta, AsignacionCuestionario,
    RespuestaCuestionario, RespuestaPregunta
)

PREGUNTAS_POR_PAGINA = 5

OPCIONES_ESCALA = {
    'likert4': [(0, 'Nunca'), (1, 'Raramente'), (2, 'A veces'), (3, 'Siempre')],
    'likert5': [(0, 'Nunca'), (1, 'Casi nunca'), (2, 'A veces'), (3, 'Frecuentemente'), (4, 'Casi siempre')],
    'sino':    [(1, 'Sí'), (0, 'No')],
    'gad7':    [(0, 'Nunca'), (1, 'Varios días'), (2, 'La mitad de los días'), (3, 'Casi cada día')],
    'pss10':   [(0, 'Nunca'), (1, 'Casi nunca'), (2, 'De vez en cuando'), (3, 'A menudo'), (4, 'Muy a menudo')],
    'phq9':    [(0, 'Ningún día'), (1, 'Varios días'), (2, 'Más de la mitad de los días'), (3, 'Casi todos los días')],
    'verdadero_falso': [(1, 'Verdadero'), (0, 'Falso')],
}

SESSION_KEY = 'quiz_parcial_{pk}'


def _session_key(pk):
    return f'quiz_parcial_{pk}'


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

    todas_las_preguntas = list(
        cuestionario.preguntas.filter(activa=True).order_by('orden', 'id')
    )
    total = len(todas_las_preguntas)
    total_paginas = max(1, (total + PREGUNTAS_POR_PAGINA - 1) // PREGUNTAS_POR_PAGINA)

    # Leer página actual de query param (o 1 por defecto)
    try:
        pagina_actual = int(request.GET.get('pagina', 1))
    except ValueError:
        pagina_actual = 1
    pagina_actual = max(1, min(pagina_actual, total_paginas))

    inicio = (pagina_actual - 1) * PREGUNTAS_POR_PAGINA
    preguntas_pagina = todas_las_preguntas[inicio: inicio + PREGUNTAS_POR_PAGINA]
    es_ultima_pagina = pagina_actual == total_paginas

    skey = _session_key(pk)

    if request.method == 'POST':
        # Leer respuestas enviadas en esta página
        respuestas_pagina = {}
        error = False

        for pregunta in preguntas_pagina:
            key = f'pregunta_{pregunta.pk}'
            if pregunta.escala in Pregunta.ESCALAS_VALOR_TEXTO:
                valor_txt = request.POST.get(key, '').strip()
                if not valor_txt:
                    messages.error(request, 'Debes completar todas las preguntas de esta página.')
                    error = True
                    break
                respuestas_pagina[str(pregunta.pk)] = {'texto': valor_txt}
            else:
                valor = request.POST.get(key)
                if valor is None:
                    messages.error(request, 'Debes responder todas las preguntas de esta página.')
                    error = True
                    break
                respuestas_pagina[str(pregunta.pk)] = {'valor': int(valor)}

        if error:
            # Volver a mostrar la misma página
            return _render_pagina(request, cuestionario, preguntas_pagina, pagina_actual,
                                  total_paginas, es_ultima_pagina, respuestas_pagina)

        # Guardar en sesión
        acumulado = request.session.get(skey, {})
        acumulado.update(respuestas_pagina)
        request.session[skey] = acumulado
        request.session.modified = True

        if es_ultima_pagina:
            # Guardar todas las respuestas en la BD
            respuesta = RespuestaCuestionario.objects.create(
                paciente=request.user,
                cuestionario=cuestionario,
            )
            for pregunta in todas_las_preguntas:
                data = acumulado.get(str(pregunta.pk))
                if data is None:
                    continue  # no debería pasar
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
            # Limpiar sesión
            if skey in request.session:
                del request.session[skey]
                request.session.modified = True

            messages.success(request, 'Se han guardado tus respuestas.')
            return redirect('cuestionarios:resultado_cuestionario', respuesta_pk=respuesta.pk)

        # Ir a la siguiente página
        return redirect(
            f"{request.path}?pagina={pagina_actual + 1}"
        )

    # GET: recuperar respuestas guardadas en sesión para pre-llenar
    acumulado = request.session.get(skey, {})
    respuestas_previas = {str(k): v for k, v in acumulado.items()}

    return _render_pagina(request, cuestionario, preguntas_pagina, pagina_actual,
                          total_paginas, es_ultima_pagina, respuestas_previas)


def _render_pagina(request, cuestionario, preguntas_pagina, pagina_actual,
                   total_paginas, es_ultima_pagina, respuestas_previas):
    preguntas_con_opciones = []
    for p in preguntas_pagina:
        if p.escala == Pregunta.ESCALA_BINARIO:
            opciones = [
                (0, p.etiqueta_opcion_1 or 'Opción 1'),
                (1, p.etiqueta_opcion_2 or 'Opción 2'),
            ]
        else:
            opciones = OPCIONES_ESCALA.get(p.escala, [])
        preguntas_con_opciones.append((p, opciones))

    return render(request, 'cuestionarios/responder_cuestionario.html', {
        'cuestionario': cuestionario,
        'preguntas_con_opciones': preguntas_con_opciones,
        'pagina_actual': pagina_actual,
        'total_paginas': total_paginas,
        'es_ultima_pagina': es_ultima_pagina,
        'pagina_anterior': pagina_actual - 1 if pagina_actual > 1 else None,
        'respuestas_previas': respuestas_previas,
        'numero_offset': (pagina_actual - 1) * PREGUNTAS_POR_PAGINA,
    })
