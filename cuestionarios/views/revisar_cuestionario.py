# Vista del administrador para revisar un cuestionario enviado a revisión
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Cuestionario


@login_required
def revisar_cuestionario(request, pk):
    if not (request.user.es_admin() or request.user.is_superuser):
        return redirect('cuentas:login')

    cuestionario = get_object_or_404(Cuestionario, pk=pk)

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'aprobar':
            publico = request.POST.get('publico') == '1'
            cuestionario.estado = Cuestionario.APROBADO
            cuestionario.publico = publico
            cuestionario.save()
            visibilidad = 'público para todos los especialistas' if publico else 'privado (solo del especialista)'
            messages.success(
                request,
                f'"{cuestionario.nombre}" fue aprobado y quedó {visibilidad}.'
            )
            return redirect('cuentas:dashboard_admin')

        elif accion == 'rechazar':
            motivo = request.POST.get('motivo', '').strip()
            if not motivo:
                messages.error(request, 'Debes ingresar un motivo de rechazo.')
            else:
                cuestionario.estado = Cuestionario.RECHAZADO
                cuestionario.publico = False
                cuestionario.save()
                messages.warning(
                    request,
                    f'"{cuestionario.nombre}" fue rechazado.'
                )
                return redirect('cuentas:dashboard_admin')

    preguntas = cuestionario.preguntas.filter(activa=True).order_by('orden', 'id')
    return render(request, 'cuestionarios/revisar_cuestionario.html', {
        'cuestionario': cuestionario,
        'preguntas': preguntas,
    })
