# HU-014 (extendido): Eliminar pregunta permanentemente
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Pregunta


@login_required
def eliminar_pregunta(request, pk):
    pregunta = get_object_or_404(
        Pregunta, pk=pk, cuestionario__especialista=request.user
    )
    cuestionario = pregunta.cuestionario

    # Solo se puede eliminar si el cuestionario es editable
    if cuestionario.estado not in (cuestionario.BORRADOR, cuestionario.RECHAZADO):
        messages.error(
            request,
            'No puedes eliminar preguntas de un cuestionario que ya fue enviado a revisión.'
        )
        return redirect('cuestionarios:detalle', pk=cuestionario.pk)

    if request.method == 'POST':
        pregunta.delete()
        messages.success(request, 'Pregunta eliminada.')
        return redirect('cuestionarios:detalle', pk=cuestionario.pk)

    return render(request, 'cuestionarios/confirmar_eliminar.html', {
        'pregunta': pregunta,
        'cuestionario': cuestionario,
    })
