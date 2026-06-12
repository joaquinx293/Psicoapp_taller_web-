# HU-013: Editar pregunta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Pregunta
from ..forms import PreguntaForm


@login_required
def editar_pregunta(request, pk):
    pregunta = get_object_or_404(
        Pregunta, pk=pk, cuestionario__especialista=request.user
    )

    if request.method == 'POST':
        form = PreguntaForm(request.POST, instance=pregunta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pregunta actualizada.')
            return redirect('cuestionarios:detalle', pk=pregunta.cuestionario.pk)
    else:
        form = PreguntaForm(instance=pregunta)

    return render(request, 'cuestionarios/editar_pregunta.html', {
        'form': form,
        'pregunta': pregunta,
    })
