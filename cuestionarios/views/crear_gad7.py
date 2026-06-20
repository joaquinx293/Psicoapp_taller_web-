# HU-019: Crear cuestionario GAD-7 precargado para el especialista
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Cuestionario, Pregunta

PREGUNTAS_GAD7 = [
    "Sentirse nervioso, ansioso o con los nervios de punta.",
    "No ser capaz de parar o controlar las preocupaciones.",
    "Preocuparse demasiado sobre diferentes cosas.",
    "Dificultad para relajarse.",
    "Estar tan inquieto que es difícil mantenerse quieto.",
    "Molestarse o irritarse fácilmente.",
    "Sentir miedo como si algo horrible fuera a pasar.",
]


@login_required
def crear_gad7(request):
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    if request.method != 'POST':
        return redirect('cuestionarios:listado')

    # Evitar duplicados: si ya existe un GAD-7 para este especialista, ir al existente
    existente = Cuestionario.objects.filter(
        especialista=request.user,
        subtipo=Cuestionario.SUBTIPO_GAD7,
    ).first()

    if existente:
        messages.info(request, 'Ya tienes un cuestionario GAD-7. Puedes editarlo aquí.')
        return redirect('cuestionarios:detalle', pk=existente.pk)

    cuestionario = Cuestionario.objects.create(
        especialista=request.user,
        nombre='GAD-7',
        descripcion=(
            'Cuestionario de 7 ítems para evaluar la severidad del trastorno de ansiedad generalizada. '
            'Recapacite sobre las ocasiones en que los ha sufrido durante las 2 últimas semanas, '
            'e indique cuál de las 4 opciones describe mejor la frecuencia con la que se ha '
            'enfrentado a esos problemas.'
        ),
        estado=Cuestionario.APROBADO,
        subtipo=Cuestionario.SUBTIPO_GAD7,
    )

    for i, texto in enumerate(PREGUNTAS_GAD7, start=1):
        Pregunta.objects.create(
            cuestionario=cuestionario,
            texto=texto,
            escala=Pregunta.ESCALA_GAD7,
            peso=1,
            orden=i,
        )

    messages.success(
        request,
        'GAD-7 creado con sus 7 preguntas estandarizadas. Puedes editarlo libremente.'
    )
    return redirect('cuestionarios:detalle', pk=cuestionario.pk)
