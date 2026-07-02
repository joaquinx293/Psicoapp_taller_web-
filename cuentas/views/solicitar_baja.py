# Vista para que el especialista solicite dar de baja su propia cuenta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from ..models import Notificacion, Usuario


@login_required
@require_http_methods(["GET", "POST"])
def solicitar_baja_especialista(request):
    """El especialista solicita que el admin desactive su cuenta."""
    if not request.user.es_especialista():
        return redirect('cuentas:redireccion')

    # Verificar si ya existe una solicitud pendiente
    ya_solicitado = Notificacion.objects.filter(
        tipo=Notificacion.TIPO_BAJA_ESPECIALISTA,
        solicitante=request.user,
        leida=False,
    ).exists()

    if ya_solicitado:
        messages.warning(
            request,
            'Ya tienes una solicitud de baja pendiente de revisión por el administrador.'
        )
        return redirect('cuentas:redireccion')

    if request.method == 'POST':
        nombre_display = request.user.get_full_name() or request.user.username

        # Contar pacientes afectados para incluir en el mensaje
        from cuestionarios.models import AsignacionCuestionario
        pacientes_count = AsignacionCuestionario.objects.filter(
            especialista=request.user, activa=True
        ).values('paciente').distinct().count()

        admins = Usuario.objects.filter(rol=Usuario.ROL_ADMIN, is_active=True)
        for admin in admins:
            Notificacion.objects.create(
                destinatario=admin,
                solicitante=request.user,
                tipo=Notificacion.TIPO_BAJA_ESPECIALISTA,
                mensaje=(
                    f'El/La especialista {nombre_display} ha solicitado dar de baja '
                    f'su cuenta. Tiene {pacientes_count} paciente(s) con cuestionarios '
                    f'activos asignados. Revisa el panel de administración para aprobar '
                    f'o rechazar esta solicitud.'
                ),
            )

        messages.success(
            request,
            'Tu solicitud de baja fue enviada al administrador. '
            'Te notificaremos cuando sea revisada.'
        )
        return redirect('cuentas:redireccion')

    return render(request, 'cuentas/solicitar_baja_especialista.html')
