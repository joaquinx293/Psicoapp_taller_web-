# Especialista: publicar y archivar sus propios cuestionarios aprobados
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Cuestionario


@login_required
def publicar_cuestionario(request, pk):
    if not request.user.es_especialista():
        return redirect('cuentas:redireccion')

    cuestionario = get_object_or_404(Cuestionario, pk=pk, especialista=request.user)

    if request.method != 'POST':
        return redirect('cuestionarios:detalle', pk=pk)

    if not cuestionario.puede_publicar():
        messages.error(request, 'Solo se pueden publicar cuestionarios en estado Aprobado.')
        return redirect('cuestionarios:detalle', pk=pk)

    cuestionario.estado = Cuestionario.PUBLICADO
    cuestionario.save()
    messages.success(request, f'"{cuestionario.nombre}" ahora está publicado y visible para tus pacientes asignados.')
    return redirect('cuestionarios:detalle', pk=pk)


@login_required
def archivar_cuestionario(request, pk):
    if not request.user.es_especialista():
        return redirect('cuentas:redireccion')

    cuestionario = get_object_or_404(Cuestionario, pk=pk, especialista=request.user)

    if request.method != 'POST':
        return redirect('cuestionarios:detalle', pk=pk)

    if not cuestionario.puede_archivar():
        messages.error(request, 'Solo se pueden archivar cuestionarios en estado Aprobado o Publicado.')
        return redirect('cuestionarios:detalle', pk=pk)

    cuestionario.estado = Cuestionario.ARCHIVADO
    cuestionario.save()
    messages.warning(request, f'"{cuestionario.nombre}" fue archivado y ya no estará disponible para nuevas respuestas.')
    return redirect('cuestionarios:detalle', pk=pk)
