# Control de acceso: especialista/admin configura permisos del paciente
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Usuario, PreferenciasVisibilidad, RecordatorioEmail


def _get_prefs(paciente):
    """Obtiene o crea las preferencias de visibilidad de un paciente."""
    prefs, _ = PreferenciasVisibilidad.objects.get_or_create(paciente=paciente)
    return prefs


def _get_recordatorio(paciente):
    """Obtiene o devuelve None el recordatorio del paciente."""
    try:
        return paciente.recordatorio_email
    except RecordatorioEmail.DoesNotExist:
        return None


@login_required
def configurar_visibilidad_paciente(request, paciente_id):
    if not (request.user.es_especialista() or request.user.es_admin() or request.user.is_superuser):
        return redirect('cuentas:redireccion')

    paciente = get_object_or_404(Usuario, pk=paciente_id, rol=Usuario.ROL_PACIENTE)
    prefs = _get_prefs(paciente)
    recordatorio = _get_recordatorio(paciente)

    # Destino de regreso según rol
    destino = 'cuentas:dashboard_admin' if request.user.es_admin() else 'gestion_usuarios:listado_pacientes'

    if request.method == 'POST':
        accion = request.POST.get('accion', 'permisos')

        if accion == 'recordatorio':
            # El especialista/admin configura el recordatorio del paciente
            sub_accion = request.POST.get('sub_accion', '')
            hora = request.POST.get('hora', '').strip()

            if sub_accion == 'desactivar' and recordatorio:
                recordatorio.activo = False
                recordatorio.save(update_fields=['activo'])
                messages.success(request, f'Recordatorio de {paciente.get_full_name() or paciente.username} desactivado.')

            elif sub_accion == 'guardar':
                if not hora:
                    messages.error(request, 'Debes indicar una hora.')
                else:
                    if recordatorio:
                        recordatorio.hora = hora
                        recordatorio.activo = True
                        recordatorio.save(update_fields=['hora', 'activo'])
                    else:
                        RecordatorioEmail.objects.create(
                            paciente=paciente,
                            hora=hora,
                            activo=True,
                        )
                    messages.success(request, f'Recordatorio configurado para {paciente.get_full_name() or paciente.username}.')

            return redirect('cuentas:configurar_visibilidad_paciente', paciente_id=paciente_id)

        else:
            # Guardar permisos (checkboxes)
            prefs.ver_historial_animo_habilitado     = 'ver_historial_animo_habilitado'     in request.POST
            prefs.ver_calendario_habilitado          = 'ver_calendario_habilitado'          in request.POST
            prefs.ver_promedio_animo_habilitado      = 'ver_promedio_animo_habilitado'      in request.POST
            prefs.editar_datos_habilitado            = 'editar_datos_habilitado'            in request.POST
            prefs.cambiar_contrasena_habilitado      = 'cambiar_contrasena_habilitado'      in request.POST
            prefs.configurar_recordatorio_habilitado = 'configurar_recordatorio_habilitado' in request.POST
            prefs.save()
            messages.success(request, f'Permisos de {paciente.get_full_name() or paciente.username} actualizados.')
            return redirect(destino)

    # Refrescar recordatorio tras POST de recordatorio
    recordatorio = _get_recordatorio(paciente)

    return render(request, 'cuentas/configurar_visibilidad_paciente.html', {
        'paciente':     paciente,
        'prefs':        prefs,
        'recordatorio': recordatorio,
        'destino':      destino,
    })
