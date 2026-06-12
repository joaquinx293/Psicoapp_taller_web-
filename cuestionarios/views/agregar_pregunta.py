# HU-012: Agregar pregunta a un cuestionario
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Cuestionario
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
            pregunta.save()
            messages.success(request, 'Pregunta agregada.')
            return redirect('cuestionarios:detalle', pk=cuestionario.pk)
    else:
        form = PreguntaForm()

    # Preguntas de otros cuestionarios del mismo especialista para importar
    from ..models import Pregunta
    preguntas_importables = Pregunta.objects.filter(
        cuestionario__especialista=request.user,
        activa=True,
    ).exclude(
        cuestionario=cuestionario
    ).select_related('cuestionario').order_by('cuestionario__nombre', 'orden')

    return render(request, 'cuestionarios/detalle.html', {
        'cuestionario': cuestionario,
        'preguntas': preguntas,
        'form': form,
        'preguntas_importables': preguntas_importables,
    })
