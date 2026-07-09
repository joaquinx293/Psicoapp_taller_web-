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

    # Solo cuestionarios aprobados/publicados o propios del especialista
    cuestionarios_qs = (
        Cuestionario.objects.filter(
            estado__in=[Cuestionario.APROBADO, Cuestionario.PUBLICADO]
        ) | Cuestionario.objects.filter(
            especialista=request.user,
            estado__in=[Cuestionario.BORRADOR, Cuestionario.APROBADO, Cuestionario.PUBLICADO]
        )
    ).distinct()

    # Asignaciones activas: {cuestionario_id: intentos_maximos}
    asignaciones_actuales = {
        a.cuestionario_id: a.intentos_maximos
        for a in AsignacionCuestionario.objects.filter(paciente=paciente, activa=True)
    }
    asignados_ids = set(asignaciones_actuales.keys())

    if request.method == 'POST':
        seleccionados = request.POST.getlist('cuestionarios')

        # Desactivar los que se quitaron
        AsignacionCuestionario.objects.filter(
            especialista=request.user,
            paciente=paciente
        ).exclude(cuestionario_id__in=seleccionados).update(activa=False)

        # Agregar o actualizar con intentos_maximos
        for cid in seleccionados:
            try:
                intentos = int(request.POST.get(f'intentos_{cid}', 1))
            except (ValueError, TypeError):
                intentos = 1
            intentos = max(0, intentos)  # 0 = ilimitado, no negativos

            AsignacionCuestionario.objects.update_or_create(
                especialista=request.user,
                paciente=paciente,
                cuestionario_id=cid,
                defaults={'activa': True, 'intentos_maximos': intentos},
            )

        messages.success(request, f'Cuestionarios de {paciente.first_name or paciente.username} actualizados.')
        return redirect('gestion_usuarios:listado_pacientes')

    # Construir lista con datos pre-cargados para el template
    cuestionarios_con_datos = [
        {
            'cuestionario': c,
            'asignado':     c.pk in asignados_ids,
            'intentos':     asignaciones_actuales.get(c.pk, 1),
        }
        for c in cuestionarios_qs
    ]

    return render(request, 'cuestionarios/asignar_cuestionario.html', {
        'paciente':                 paciente,
        'cuestionarios_con_datos':  cuestionarios_con_datos,
        'asignados_ids':            asignados_ids,
    })
