# Especialista asigna cuestionarios a un paciente
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Cuestionario, AsignacionCuestionario
from cuentas.models import Usuario


@login_required
def asignar_cuestionario(request, paciente_pk):
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    paciente = get_object_or_404(Usuario, pk=paciente_pk, rol=Usuario.ROL_PACIENTE)

    # Solo cuestionarios aprobados o propios del especialista
    cuestionarios_disponibles = Cuestionario.objects.filter(
        estado=Cuestionario.APROBADO
    ) | Cuestionario.objects.filter(
        especialista=request.user,
        estado__in=[Cuestionario.BORRADOR, Cuestionario.APROBADO, Cuestionario.RECHAZADO]
    )
    cuestionarios_disponibles = cuestionarios_disponibles.distinct()

    asignados_ids = AsignacionCuestionario.objects.filter(
        paciente=paciente, activa=True
    ).values_list('cuestionario_id', flat=True)

    if request.method == 'POST':
        seleccionados = request.POST.getlist('cuestionarios')

        # Desactivar los que se quitaron
        AsignacionCuestionario.objects.filter(
            especialista=request.user,
            paciente=paciente
        ).exclude(cuestionario_id__in=seleccionados).update(activa=False)

        # Agregar o reactivar los nuevos
        for cid in seleccionados:
            AsignacionCuestionario.objects.update_or_create(
                especialista=request.user,
                paciente=paciente,
                cuestionario_id=cid,
                defaults={'activa': True}
            )

        messages.success(request, f'Cuestionarios de {paciente.first_name or paciente.username} actualizados.')
        return redirect('gestion_usuarios:listado_pacientes')

    return render(request, 'cuestionarios/asignar_cuestionario.html', {
        'paciente': paciente,
        'cuestionarios_disponibles': cuestionarios_disponibles,
        'asignados_ids': list(asignados_ids),
    })
