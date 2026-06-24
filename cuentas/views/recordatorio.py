# HU-027: Configurar recordatorio diario por correo electrónico
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from ..models import RecordatorioEmail


@login_required
@require_http_methods(["POST"])
def configurar_recordatorio(request):
    """Activa, desactiva o actualiza la hora del recordatorio del paciente."""
    if not request.user.es_paciente():
        return redirect('cuentas:redireccion')

    accion = request.POST.get('accion', '')
    hora = request.POST.get('hora', '').strip()

    try:
        rec = request.user.recordatorio_email
    except RecordatorioEmail.DoesNotExist:
        rec = None

    if accion == 'desactivar' and rec:
        rec.activo = False
        rec.save(update_fields=['activo'])
        messages.success(request, 'Recordatorio desactivado.')

    elif accion == 'guardar':
        if not hora:
            messages.error(request, 'Debes indicar una hora.')
        else:
            if rec:
                rec.hora = hora
                rec.activo = True
                rec.save(update_fields=['hora', 'activo'])
            else:
                RecordatorioEmail.objects.create(
                    paciente=request.user,
                    hora=hora,
                    activo=True,
                )
            messages.success(request, 'Recordatorio configurado correctamente.')

    return redirect('cuentas:perfil_paciente')
