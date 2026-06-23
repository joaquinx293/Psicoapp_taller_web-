# HU-025: Configurar pregunta diaria de seguimiento por paciente
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from cuentas.models import PreguntaDiaria, Usuario


@login_required
@require_http_methods(["GET", "POST"])
def pregunta_diaria(request, paciente_id):
    """El especialista configura, modifica o desactiva la pregunta diaria de un paciente."""
    if not (request.user.es_especialista() or request.user.es_admin() or request.user.is_superuser):
        return redirect('cuentas:login')

    paciente = get_object_or_404(Usuario, pk=paciente_id, rol=Usuario.ROL_PACIENTE)

    # Intentar obtener la config existente
    try:
        config = paciente.pregunta_diaria
    except PreguntaDiaria.DoesNotExist:
        config = None

    if request.method == 'POST':
        accion = request.POST.get('accion', 'guardar')

        if accion == 'desactivar' and config:
            config.activa = False
            config.save()
            messages.success(request, 'Pregunta diaria desactivada.')
            return redirect('gestion_usuarios:pregunta_diaria', paciente_id=paciente_id)

        if accion == 'activar' and config:
            config.activa = True
            config.save()
            messages.success(request, 'Pregunta diaria reactivada.')
            return redirect('gestion_usuarios:pregunta_diaria', paciente_id=paciente_id)

        # Guardar / actualizar
        texto = request.POST.get('texto', '').strip()
        hora_inicio = request.POST.get('hora_inicio', '').strip()

        if not texto:
            messages.error(request, 'El texto de la pregunta no puede estar vacío.')
        elif len(texto) > 200:
            messages.error(request, 'El texto no puede superar los 200 caracteres.')
        elif not hora_inicio:
            messages.error(request, 'Debes indicar la hora de inicio.')
        else:
            if config:
                config.texto = texto
                config.hora_inicio = hora_inicio
                config.activa = True
                config.especialista = request.user
                config.save()
                messages.success(request, 'Pregunta diaria actualizada.')
            else:
                PreguntaDiaria.objects.create(
                    paciente=paciente,
                    especialista=request.user,
                    texto=texto,
                    hora_inicio=hora_inicio,
                    activa=True,
                )
                messages.success(request, 'Pregunta diaria configurada.')
            return redirect('gestion_usuarios:pregunta_diaria', paciente_id=paciente_id)

    # Historial de respuestas (HU-026 — si el modelo ya existe)
    respuestas = []
    try:
        from cuentas.models import RespuestaPreguntaDiaria
        if config:
            respuestas = RespuestaPreguntaDiaria.objects.filter(
                pregunta_diaria=config
            ).order_by('-fecha')[:30]
    except ImportError:
        pass

    return render(request, 'gestion_usuarios/pregunta_diaria.html', {
        'paciente': paciente,
        'config': config,
        'respuestas': respuestas,
    })
