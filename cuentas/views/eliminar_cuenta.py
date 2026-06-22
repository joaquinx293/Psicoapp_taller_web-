# HU-010: Solicitar eliminación de cuenta con anonimización
import uuid

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from ..models import Notificacion, RegistroAnimo, Usuario


@login_required
@require_http_methods(["GET", "POST"])
def confirmar_eliminacion(request):
    """Pide contraseña y anonimiza la cuenta del paciente."""
    if not request.user.es_paciente():
        return redirect('cuentas:redireccion')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        if not request.user.check_password(password):
            messages.error(request, 'Contraseña incorrecta. Intenta de nuevo.')
            return render(request, 'cuentas/confirmar_eliminacion.html')

        paciente = request.user

        # Notificar al especialista ANTES de anonimizar
        nombre_display = paciente.get_full_name() or paciente.username
        try:
            invitacion = paciente.invitacion_recibida
            if invitacion and invitacion.especialista:
                Notificacion.objects.create(
                    destinatario=invitacion.especialista,
                    mensaje=(
                        f'El paciente {nombre_display} ha solicitado la eliminación '
                        f'de su cuenta. Sus datos personales han sido anonimizados '
                        f'y sus respuestas a cuestionarios se conservan sin identificación.'
                    ),
                )
        except Exception:
            pass  # Sin invitación o especialista, continuar igual

        # Anonimizar datos identificables
        uid = uuid.uuid4().hex[:10]
        paciente.username = f'anonimo_{uid}'
        paciente.first_name = ''
        paciente.last_name = ''
        paciente.email = ''
        paciente.fecha_nacimiento = None
        paciente.motivo_rechazo = None
        paciente.estado = Usuario.INACTIVO
        paciente.is_active = False
        paciente.set_unusable_password()
        paciente.save()

        # Eliminar registros personales (estado de ánimo)
        RegistroAnimo.objects.filter(paciente=paciente).delete()

        # Eliminar asignaciones de cuestionarios
        from cuestionarios.models import AsignacionCuestionario
        AsignacionCuestionario.objects.filter(paciente=paciente).delete()

        # Cerrar sesión y redirigir
        logout(request)
        return redirect('cuentas:cuenta_eliminada')

    return render(request, 'cuentas/confirmar_eliminacion.html')


def cuenta_eliminada(request):
    """Página de confirmación post-eliminación. No requiere autenticación."""
    return render(request, 'cuentas/cuenta_eliminada.html')
