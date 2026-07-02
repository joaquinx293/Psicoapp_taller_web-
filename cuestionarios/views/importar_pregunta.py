# Val-4: Copiar una pregunta existente de otro cuestionario
# — verifica que no exista ya una pregunta con el mismo texto en el destino
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

        # Val-4: verificar que el texto no exista ya en el cuestionario destino
        texto_duplicado = cuestionario.preguntas.filter(
            texto__iexact=origen.texto, activa=True
        ).exists()

        if texto_duplicado:
            messages.error(
                request,
                f'La pregunta "{origen.texto[:60]}" ya existe en este cuestionario. '
                f'No se puede importar una pregunta duplicada.'
            )
            return redirect('cuestionarios:detalle', pk=pk)

        # Crear copia en el cuestionario destino
        nuevo_orden = cuestionario.preguntas.filter(activa=True).count() + 1
        Pregunta.objects.create(
            cuestionario=cuestionario,
            texto=origen.texto,
            escala=origen.escala,
            peso=origen.peso,
            orden=nuevo_orden,
            invertir=origen.invertir,
            etiqueta_opcion_1=origen.etiqueta_opcion_1,
            etiqueta_opcion_2=origen.etiqueta_opcion_2,
        )
        messages.success(request, f'Pregunta "{origen.texto[:50]}" importada.')

    return redirect('cuestionarios:detalle', pk=pk)
