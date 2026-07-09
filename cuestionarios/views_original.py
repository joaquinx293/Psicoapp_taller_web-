from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cuestionario, Pregunta
from .forms import CuestionarioForm, PreguntaForm


@login_required
def listado_cuestionarios(request):
    """Lista los cuestionarios del especialista"""
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    cuestionarios = Cuestionario.objects.filter(especialista=request.user)
    return render(request, 'cuestionarios/listado.html', {
        'cuestionarios': cuestionarios
    })


@login_required
def crear_cuestionario(request):
    """HU-011: crear un cuestionario nuevo"""
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


@login_required
def detalle_cuestionario(request, pk):
    """Ver un cuestionario y sus preguntas + agregar pregunta (HU-012)"""
    cuestionario = get_object_or_404(
        Cuestionario, pk=pk, especialista=request.user
    )
    preguntas = cuestionario.preguntas.filter(activa=True)

    if request.method == 'POST':
        form = PreguntaForm(request.POST)
        if form.is_valid():
            pregunta = form.save(commit=False)
            pregunta.cuestionario = cuestionario
            pregunta.orden = preguntas.count() + 1
            pregunta.save()
            messages.success(request, 'Pregunta agregada.')
            return redirect('cuestionarios:detalle', pk=cuestionario.pk)
    else:
        form = PreguntaForm()

    return render(request, 'cuestionarios/detalle.html', {
        'cuestionario': cuestionario,
        'preguntas': preguntas,
        'form': form,
    })


@login_required
def editar_pregunta(request, pk):
    """HU-013: editar una pregunta"""
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


@login_required
def desactivar_pregunta(request, pk):
    """HU-014: desactivar (borrado logico) una pregunta"""
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