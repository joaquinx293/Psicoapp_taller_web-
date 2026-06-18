# Especialista: explorar cuestionarios públicos y copiarlos
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Cuestionario, Pregunta
from .seed_sistema import asegurar_cuestionarios_sistema


@login_required
def cuestionarios_publicos(request, pk=None):
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    # Copiar un cuestionario público al listado propio
    if request.method == 'POST' and pk:
        original = get_object_or_404(
            Cuestionario, pk=pk, publico=True, estado=Cuestionario.APROBADO
        )

        nombre_copia = f'{original.nombre} (copia)'
        ya_existe = Cuestionario.objects.filter(
            especialista=request.user,
            nombre=nombre_copia,
        ).exists()

        if ya_existe:
            messages.info(request, 'Ya tienes una copia de ese cuestionario en tu listado.')
            return redirect('cuestionarios:cuestionarios_publicos')

        copia = Cuestionario.objects.create(
            especialista=request.user,
            nombre=nombre_copia,
            descripcion=original.descripcion,
            estado=Cuestionario.BORRADOR,
            subtipo=original.subtipo,
            publico=False,
        )
        for pregunta in original.preguntas.filter(activa=True).order_by('orden', 'id'):
            Pregunta.objects.create(
                cuestionario=copia,
                texto=pregunta.texto,
                escala=pregunta.escala,
                peso=pregunta.peso,
                orden=pregunta.orden,
                etiqueta_opcion_1=pregunta.etiqueta_opcion_1,
                etiqueta_opcion_2=pregunta.etiqueta_opcion_2,
                invertir=pregunta.invertir,
            )

        messages.success(
            request,
            f'Se copió "{original.nombre}" a tus cuestionarios como borrador. '
            'Puedes editarlo y enviarlo a revisión cuando quieras.'
        )
        return redirect('cuestionarios:listado')

    # Asegurar que las plantillas del sistema existan
    asegurar_cuestionarios_sistema()

    publicos = Cuestionario.objects.filter(
        publico=True, estado=Cuestionario.APROBADO
    ).order_by('especialista', 'nombre')

    return render(request, 'cuestionarios/cuestionarios_publicos.html', {
        'publicos': publicos,
    })
