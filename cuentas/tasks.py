# HU-027: Tarea de envío de recordatorios diarios por correo electrónico
import logging
from datetime import date

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


def enviar_recordatorios_email():
    """
    Envía recordatorios de registro emocional a los pacientes que:
      - Tienen el recordatorio activo.
      - La hora configurada ya pasó hoy.
      - No recibieron email hoy (ultimo_envio != hoy).
      - Aún no registraron su estado de ánimo hoy.
    Se ejecuta cada minuto vía APScheduler.
    """
    # Importaciones aquí para evitar problemas en apps.py ready()
    from .models import RecordatorioEmail, RegistroAnimo

    hoy = date.today()
    ahora = timezone.localtime().time()

    pendientes = RecordatorioEmail.objects.filter(
        activo=True,
        hora__lte=ahora,
    ).exclude(ultimo_envio=hoy).select_related('paciente')

    for rec in pendientes:
        paciente = rec.paciente

        # No enviar si el paciente ya no está activo
        if not paciente.is_active:
            continue

        # No enviar si ya registró su ánimo hoy
        if RegistroAnimo.objects.filter(paciente=paciente, fecha=hoy).exists():
            # Marcar igualmente para no revisarlo de nuevo hoy
            rec.ultimo_envio = hoy
            rec.save(update_fields=['ultimo_envio'])
            continue

        if not paciente.email:
            continue

        try:
            asunto = 'PsicoApp — Recuerda registrar tu estado de ánimo de hoy'
            cuerpo_html = render_to_string(
                'cuentas/email_recordatorio.html',
                {'paciente': paciente},
            )
            cuerpo_txt = (
                f'Hola {paciente.first_name or paciente.username},\n\n'
                f'Te recordamos registrar tu estado de ánimo de hoy en PsicoApp.\n\n'
                f'Ingresa en: http://127.0.0.1:8000/cuentas/animo/\n\n'
                f'— El equipo de PsicoApp'
            )
            send_mail(
                subject=asunto,
                message=cuerpo_txt,
                from_email=None,  # Usa DEFAULT_FROM_EMAIL
                recipient_list=[paciente.email],
                html_message=cuerpo_html,
                fail_silently=False,
            )
            rec.ultimo_envio = hoy
            rec.save(update_fields=['ultimo_envio'])
            logger.info(f'Recordatorio enviado a {paciente.email}')
        except Exception as exc:
            logger.error(f'Error enviando recordatorio a {paciente.email}: {exc}')
