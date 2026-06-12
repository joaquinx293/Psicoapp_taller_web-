# HU-011: Crear cuestionario personalizado
# HU-016: Listado incluye cuestionarios aprobados de todos los especialistas
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Cuestionario
from ..forms import CuestionarioForm


@login_required
def listado_cuestionarios(request):
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    mis_cuestionarios = Cuestionario.objects.filter(especialista=request.user)
    cuestionarios_aprobados = Cuestionario.objects.filter(
        estado=Cuestionario.APROBADO
    ).exclude(especialista=request.user)

    return render(request, 'cuestionarios/listado.html', {
        'mis_cuestionarios': mis_cuestionarios,
        'cuestionarios_aprobados': cuestionarios_aprobados,
    })


@login_required
def crear_cuestionario(request):
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    if request.method == 'POST':
        form = CuestionarioForm(request.POST)
        if form.is_valid():
            cuestionario = form.save(commit=False)
            cuestionario.especialista = request.user
            cuestionario.estado = Cuestionario.BORRADOR
            cuestionario.save()
            messages.success(request, 'Cuestionario creado. Ahora agrega preguntas.')
            return redirect('cuestionarios:detalle', pk=cuestionario.pk)
    else:
        form = CuestionarioForm()

    return render(request, 'cuestionarios/crear.html', {'form': form})
