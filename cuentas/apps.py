import os
from django.apps import AppConfig


class CuentasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cuentas'

    def ready(self):
        """Inicia el scheduler de APScheduler al arrancar el servidor."""
        import sys

        # Solo correr en runserver, no en migrate/makemigrations/etc.
        if 'runserver' not in sys.argv:
            return

        # En desarrollo, Django lanza dos procesos (reloader + worker).
        # Solo iniciar el scheduler en el proceso hijo (RUN_MAIN=true).
        if os.environ.get('RUN_MAIN') != 'true':
            return

        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.interval import IntervalTrigger
            import atexit

            from .tasks import enviar_recordatorios_email

            scheduler = BackgroundScheduler()
            scheduler.add_job(
                enviar_recordatorios_email,
                trigger=IntervalTrigger(minutes=1),
                id='enviar_recordatorios_email',
                name='Recordatorios diarios de estado de ánimo',
                replace_existing=True,
            )
            scheduler.start()
            atexit.register(lambda: scheduler.shutdown(wait=False))
        except ImportError:
            import logging
            logging.getLogger(__name__).warning(
                'APScheduler no está instalado. '
                'Ejecuta: pip install apscheduler'
            )
