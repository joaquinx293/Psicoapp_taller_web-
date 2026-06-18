# Especialista asigna cuestionarios a un paciente ANTES de que se registre
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Cuestionario, AsignacionPendiente
from gestion_usuarios.models import InvitacionPaciente


@login_required
def asignar_pendiente(request, invitacion_pk):
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    invitacion = get_object_or_404(
        InvitacionPaciente,
        pk=invitacion_pk,
        especialista=request.user,
    )

    # Si ya se registró, redirigir a la asignación normal
    if invitacion.paciente:
        return redirect('cuestionarios:asignar_cuestionario', paciente_pk=invitacion.paciente.pk)

    cuestionarios_disponibles = (
        Cuestionario.objects.filter(estado=Cuestionario.APROBADO) |
        Cuestionario.objects.filter(
            especialista=request.user,
            estado__in=[Cuestionario.BORRADOR, Cuestionario.APROBADO, Cuestionario.RECHAZADO]
        )
    ).distinct()

    asignados_ids = AsignacionPendiente.objects.filter(
        invitacion=invitacion
    ).values_list('cuestionario_id', flat=True)

    if request.method == 'POST':
        seleccionados = request.POST.getlist('cuestionarios')

        # Quitar los que se desmarcaron
        AsignacionPendiente.objects.filter(
            especialista=request.user,
            invitacion=invitacion,
        ).exclude(cuestionario_id__in=seleccionados).delete()

        # Agregar los nuevos
        for cid in seleccionados:
            AsignacionPendiente.objects.get_or_create(
                especialista=request.user,
                invitacion=invitacion,
                cuestionario_id=cid,
            )

        messages.success(
            request,
            f'Cuestionarios precargados para {invitacion.nombre_paciente}. '
            'Se asignarán automáticamente cuando complete su registro.'
        )
        return redirect('gestion_usuarios:listado_pacientes')

    return render(request, 'cuestionarios/asignar_pendiente.html', {
        'invitacion': invitacion,
        'cuestionarios_disponibles': cuestionarios_disponibles,
        'asignados_ids': list(asignados_ids),
    })
