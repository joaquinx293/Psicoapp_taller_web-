# HU-026: Responder pregunta diaria de seguimiento
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from ..models import RespuestaPreguntaDiaria
@login_required
def responder_pregunta_diaria(request):
    """El paciente responde su pregunta diaria (si está disponible y no la ha respondido hoy)."""
    if not request.user.es_paciente():
        return redirect('cuentas:redireccion')

    try:
        config = request.user.pregunta_diaria
    except Exception:
        messages.error(request, 'No tienes una pregunta diaria configurada.')
        return redirect('cuentas:perfil_paciente')

    if not config.activa:
        messages.error(request, 'Tu pregunta diaria está desactivada.')
        return redirect('cuentas:perfil_paciente')

    hoy = timezone.localdate()
    ahora = timezone.localtime().time()

    # Verificar horario
    if ahora < config.hora_inicio:
        messages.info(
            request,
            f'La pregunta estará disponible a partir de las {config.hora_inicio.strftime("%H:%M")}.'
        )
        return redirect('cuentas:perfil_paciente')

    # Verificar si ya respondió hoy
    ya_respondio = RespuestaPreguntaDiaria.objects.filter(
        pregunta_diaria=config, fecha=hoy
    ).exists()

    if ya_respondio:
        messages.info(request, 'Ya respondiste la pregunta de hoy.')
        return redirect('cuentas:perfil_paciente')

    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        if not texto:
            messages.error(request, 'La respuesta no puede estar vacía.')
        elif len(texto) > 500:
            messages.error(request, 'La respuesta no puede superar los 500 caracteres.')
        else:
            RespuestaPreguntaDiaria.objects.create(
                pregunta_diaria=config,
                paciente=request.user,
                fecha=hoy,
                texto=texto,
            )
            messages.success(request, 'Respuesta guardada.')
            return redirect('cuentas:perfil_paciente')

    return render(request, 'cuentas/responder_pregunta_diaria.html', {
        'config': config,
        'hoy': hoy,
    })


@login_required
def historial_pregunta_diaria(request):
    """Historial de respuestas anteriores del paciente a su pregunta diaria."""
    if not request.user.es_paciente():
        return redirect('cuentas:redireccion')

    try:
        config = request.user.pregunta_diaria
    except Exception:
        config = None

    respuestas = []
    if config:
        respuestas = RespuestaPreguntaDiaria.objects.filter(
            pregunta_diaria=config
        ).order_by('-fecha')

    return render(request, 'cuentas/historial_pregunta_diaria.html', {
        'config': config,
        'respuestas': respuestas,
    })
