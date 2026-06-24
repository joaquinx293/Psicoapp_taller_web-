# Crea las plantillas del sistema (GAD-7 y PSS-10) si no existen.
# Se llama desde cuestionarios_publicos al cargar la página.
from ..models import Cuestionario, Pregunta


# ─── GAD-7 ────────────────────────────────────────────────────────────────────

_GAD7_PREGUNTAS = [
    '¿Con qué frecuencia se ha sentido nervioso, ansioso o muy alterado?',
    '¿Con qué frecuencia no ha podido dejar de preocuparse o no ha podido controlar su preocupación?',
    '¿Con qué frecuencia se ha preocupado demasiado por diferentes cosas?',
    '¿Con qué frecuencia ha tenido dificultad para relajarse?',
    '¿Con qué frecuencia se ha sentido tan intranquilo que no ha podido quedarse quieto?',
    '¿Con qué frecuencia se ha molestado o irritado fácilmente?',
    '¿Con qué frecuencia ha sentido miedo como si algo terrible fuera a ocurrir?',
]

# ─── PSS-10 ───────────────────────────────────────────────────────────────────

_PSS10_PREGUNTAS = [
    # (texto, invertir)
    ('En el último mes, ¿con qué frecuencia ha estado afectado por algo que ha ocurrido inesperadamente?', False),
    ('En el último mes, ¿con qué frecuencia se ha sentido incapaz de controlar las cosas importantes en su vida?', False),
    ('En el último mes, ¿con qué frecuencia se ha sentido nervioso o estresado?', False),
    ('En el último mes, ¿con qué frecuencia ha estado seguro sobre su capacidad para manejar sus problemas personales?', True),
    ('En el último mes, ¿con qué frecuencia ha sentido que las cosas le van bien?', True),
    ('En el último mes, ¿con qué frecuencia ha sentido que no podía afrontar todas las cosas que tenía que hacer?', True),
    ('En el último mes, ¿con qué frecuencia ha podido controlar las dificultades de su vida?', True),
    ('En el último mes, ¿con qué frecuencia se ha sentido que tenía todo bajo control?', False),
    ('En el último mes, ¿con qué frecuencia ha estado enfadado porque las cosas que le han ocurrido estaban fuera de su control?', False),
    ('En el último mes, ¿con qué frecuencia ha sentido que las dificultades se acumulan tanto que no puede superarlas?', False),
]


def asegurar_cuestionarios_sistema():
    """Crea GAD-7 y PSS-10 como plantillas del sistema si no existen."""
    _asegurar_gad7()
    _asegurar_pss10()


def _asegurar_gad7():
    existe = Cuestionario.objects.filter(
        especialista__isnull=True,
        subtipo=Cuestionario.SUBTIPO_GAD7,
    ).exists()
    if existe:
        return

    c = Cuestionario.objects.create(
        especialista=None,
        nombre='GAD-7 — Evaluación de ansiedad generalizada',
        descripcion=(
            'Escala estandarizada de 7 preguntas para evaluar el nivel de '
            'ansiedad generalizada durante las últimas dos semanas. '
            'Clasificación: Mínimo (0-4), Leve (5-9), Moderado (10-14), Severo (15-21).'
        ),
        estado=Cuestionario.APROBADO,
        subtipo=Cuestionario.SUBTIPO_GAD7,
        publico=True,
    )
    for i, texto in enumerate(_GAD7_PREGUNTAS, start=1):
        Pregunta.objects.create(
            cuestionario=c,
            texto=texto,
            escala=Pregunta.ESCALA_GAD7,
            peso=1,
            orden=i,
        )


def _asegurar_pss10():
    existe = Cuestionario.objects.filter(
        especialista__isnull=True,
        subtipo=Cuestionario.SUBTIPO_PSS10,
    ).exists()
    if existe:
        return

    c = Cuestionario.objects.create(
        especialista=None,
        nombre='PSS-10 — Escala de estrés percibido',
        descripcion=(
            'Versión de 10 ítems de la Escala de Estrés Percibido (Cohen, 1983). '
            'Evalúa el nivel de estrés percibido durante el último mes. '
            'Clasificación: Bajo (0-13), Moderado (14-26), Alto (27-40).'
        ),
        estado=Cuestionario.APROBADO,
        subtipo=Cuestionario.SUBTIPO_PSS10,
        publico=True,
    )
    for i, (texto, invertir) in enumerate(_PSS10_PREGUNTAS, start=1):
        Pregunta.objects.create(
            cuestionario=c,
            texto=texto,
            escala=Pregunta.ESCALA_PSS10,
            peso=1,
            orden=i,
            invertir=invertir,
        )
