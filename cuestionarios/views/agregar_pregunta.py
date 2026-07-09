# HU-012: Agregar pregunta a un cuestionario
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Cuestionario, Pregunta
from ..forms import PreguntaForm


@login_required
def detalle_cuestionario(request, pk):
    """Muestra el cuestionario y sus preguntas activas.
    El POST agrega una nueva pregunta (HU-012)."""
    cuestionario = get_object_or_404(
        Cuestionario, pk=pk, especialista=request.user
    )
    preguntas = cuestionario.preguntas.filter(activa=True)

    if request.method == 'POST':
        form = PreguntaForm(request.POST)
        if form.is_valid():
            pregunta = form.save(commit=False)
            pregunta.cuestionario = cuestionario
            pregunta.orden = preguntas.count() + 1
            try:
                pregunta.save()
                messages.success(request, 'Pregunta agregada.')
                return redirect('cuestionarios:detalle', pk=cuestionario.pk)
            except IntegrityError:
                # Val-1: el UniqueConstraint (cuestionario, texto) lo detecta aquí
                form.add_error(
                    'texto',
                    'Ya existe una pregunta con ese texto en este cuestionario. '
                    'Escribe un texto diferente.'
                )
    else:
        form = PreguntaForm()

    # ¿El especialista tiene otros cuestionarios con preguntas? (para mostrar/ocultar sección importar)
    tiene_otros = Pregunta.objects.filter(
        cuestionario__especialista=request.user,
        activa=True,
    ).exclude(cuestionario=cuestionario).exists()

    return render(request, 'cuestionarios/detalle.html', {
        'cuestionario': cuestionario,
        'preguntas': preguntas,
        'form': form,
        'tiene_otros': tiene_otros,
    })
