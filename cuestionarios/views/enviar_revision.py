# HU-016: Enviar cuestionario a revisión del administrador
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Cuestionario


@login_required
def enviar_a_revision(request, pk):
    cuestionario = get_object_or_404(
        Cuestionario, pk=pk, especialista=request.user
    )

    if not cuestionario.puede_enviar_revision():
        messages.error(
            request,
            'Este cuestionario no puede enviarse a revisión en su estado actual.'
        )
        return redirect('cuestionarios:detalle', pk=pk)

    if cuestionario.cantidad_preguntas_activas() == 0:
        messages.error(
            request,
            'Debes agregar al menos una pregunta antes de enviar a revisión.'
        )
        return redirect('cuestionarios:detalle', pk=pk)

    if request.method == 'POST':
        cuestionario.estado = Cuestionario.EN_REVISION
        cuestionario.save()
        messages.success(
            request,
            f'"{cuestionario.nombre}" enviado a revisión. '
            f'El administrador lo revisará pronto.'
        )
        return redirect('cuestionarios:listado')

    return redirect('cuestionarios:detalle', pk=pk)
