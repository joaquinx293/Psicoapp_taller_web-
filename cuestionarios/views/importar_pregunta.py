# Copiar una pregunta existente de otro cuestionario
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Cuestionario, Pregunta


@login_required
def importar_pregunta(request, pk):
    """Copia una pregunta de otro cuestionario al cuestionario actual."""
    cuestionario = get_object_or_404(
        Cuestionario, pk=pk, especialista=request.user
    )

    if cuestionario.estado not in (Cuestionario.BORRADOR, Cuestionario.RECHAZADO):
        messages.error(request, 'No puedes modificar este cuestionario en su estado actual.')
        return redirect('cuestionarios:detalle', pk=pk)

    if request.method == 'POST':
        pregunta_origen_pk = request.POST.get('pregunta_id')
        if not pregunta_origen_pk:
            messages.error(request, 'Selecciona una pregunta.')
            return redirect('cuestionarios:detalle', pk=pk)

        origen = get_object_or_404(
            Pregunta,
            pk=pregunta_origen_pk,
            cuestionario__especialista=request.user,
            activa=True
        )

        # Crear copia en el cuestionario destino
        nuevo_orden = cuestionario.preguntas.filter(activa=True).count() + 1
        Pregunta.objects.create(
            cuestionario=cuestionario,
            texto=origen.texto,
            escala=origen.escala,
            peso=origen.peso,
            orden=nuevo_orden,
        )
        messages.success(request, f'Pregunta "{origen.texto[:50]}" importada.')

    return redirect('cuestionarios:detalle', pk=pk)
