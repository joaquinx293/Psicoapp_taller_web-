# Especialista asigna cuestionarios a un paciente
import json
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

        messages.success(
            request,
            f'Cuestionarios de {paciente.first_name or paciente.username} actualizados.'
        )
        return redirect('gestion_usuarios:listado_pacientes')

    # GET: solo carga asignaciones activas actuales (no todo el catálogo)
    asignaciones = AsignacionCuestionario.objects.filter(
        especialista=request.user,
        paciente=paciente,
        activa=True,
    ).select_related('cuestionario').order_by('cuestionario__nombre')

    asignados_json = json.dumps([
        {
            'id': a.cuestionario_id,
            'nombre': a.cuestionario.nombre,
            'intentos': a.intentos_maximos,
        }
        for a in asignaciones
    ], ensure_ascii=False)

    return render(request, 'cuestionarios/asignar_cuestionario.html', {
        'paciente':      paciente,
        'asignados_json': asignados_json,
    })
