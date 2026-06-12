# HU-014: Desactivar pregunta (borrado lógico)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Pregunta


@login_required
def desactivar_pregunta(request, pk):
    pregunta = get_object_or_404(
        Pregunta, pk=pk, cuestionario__especialista=request.user
    )
    cuestionario_pk = pregunta.cuestionario.pk

    if request.method == 'POST':
        pregunta.activa = False
        pregunta.save()
        messages.success(request, 'Pregunta desactivada.')
        return redirect('cuestionarios:detalle', pk=cuestionario_pk)

    return render(request, 'cuestionarios/confirmar_desactivar.html', {
        'pregunta': pregunta,
    })
