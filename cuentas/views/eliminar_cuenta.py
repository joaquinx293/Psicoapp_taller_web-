# HU-010: Solicitar eliminación de cuenta (flujo con aprobación del admin)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from ..models import Notificacion, Usuario


@login_required
@require_http_methods(["GET", "POST"])
def confirmar_eliminacion(request):
    """Paciente solicita la eliminación de su cuenta. Se crea una notificación al admin."""
    if not request.user.es_paciente():
        return redirect('cuentas:redireccion')

    # Verificar si ya existe una solicitud pendiente
    ya_solicitado = Notificacion.objects.filter(
        tipo=Notificacion.TIPO_BAJA_PACIENTE,
        solicitante=request.user,
        leida=False,
    ).exists()

    if ya_solicitado:
        messages.warning(
            request,
            'Ya tienes una solicitud de eliminación de cuenta pendiente de revisión.'
        )
        return redirect('cuentas:perfil_paciente')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        if not request.user.check_password(password):
            messages.error(request, 'Contraseña incorrecta. Intenta de nuevo.')
            return render(request, 'cuentas/confirmar_eliminacion.html')

        paciente = request.user
        nombre_display = paciente.get_full_name() or paciente.username

        # Crear notificación para todos los administradores activos
        admins = Usuario.objects.filter(rol=Usuario.ROL_ADMIN, is_active=True)
        for admin in admins:
            Notificacion.objects.create(
                destinatario=admin,
                solicitante=paciente,
                tipo=Notificacion.TIPO_BAJA_PACIENTE,
                mensaje=(
                    f'El paciente {nombre_display} ha solicitado la eliminación '
                    f'de su cuenta. Revisa la sección de solicitudes de baja en el panel '
                    f'de administración para aprobar o rechazar esta solicitud.'
                ),
            )

        messages.success(
            request,
            'Tu solicitud fue enviada. El administrador la revisará a la brevedad.'
        )
        return redirect('cuentas:cuenta_en_revision')

    return render(request, 'cuentas/confirmar_eliminacion.html')


def cuenta_eliminada(request):
    """Página informativa post-eliminación (cuando el admin aprueba y anonimiza)."""
    return render(request, 'cuentas/cuenta_eliminada.html')


def cuenta_en_revision(request):
    """Página de confirmación: la solicitud de baja fue enviada y está pendiente."""
    return render(request, 'cuentas/cuenta_en_revision.html')
