# HU-016: Solicitar aprobación de cuestionario al administrador
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
            'Solo puedes solicitar aprobación de cuestionarios en estado Borrador.'
        )
        return redirect('cuestionarios:detalle', pk=pk)

    if cuestionario.cantidad_preguntas_activas() == 0:
        messages.error(
            request,
            'Debes agregar al menos una pregunta antes de solicitar aprobación.'
        )
        return redirect('cuestionarios:detalle', pk=pk)

    # Val-2: verificar que no exista otro cuestionario aprobado/publicado del mismo
    # especialista con exactamente las mismas preguntas
    textos_actuales = set(
        cuestionario.preguntas.filter(activa=True).values_list('texto', flat=True)
    )
    otros = Cuestionario.objects.filter(
        especialista=request.user,
        estado__in=[Cuestionario.APROBADO, Cuestionario.PUBLICADO],
    ).exclude(pk=cuestionario.pk)

    for otro in otros:
        textos_otro = set(otro.preguntas.filter(activa=True).values_list('texto', flat=True))
        if textos_otro == textos_actuales and len(textos_otro) == len(textos_actuales):
            messages.error(
                request,
                f'Ya existe un cuestionario aprobado con estas preguntas: '
                f'"{otro.nombre}" (ID: {otro.id_cuestionario or "sin ID"}). '
                f'Modifica las preguntas antes de solicitar aprobación.'
            )
            return redirect('cuestionarios:detalle', pk=pk)

    if request.method == 'POST':
        # El cuestionario permanece en borrador; el admin lo verá en el dashboard
        # y podrá aprobarlo directamente.
        messages.success(
            request,
            f'"{cuestionario.nombre}" fue enviado para aprobación. '
            f'El administrador lo revisará pronto.'
        )
        return redirect('cuestionarios:listado')

    return redirect('cuestionarios:detalle', pk=pk)
