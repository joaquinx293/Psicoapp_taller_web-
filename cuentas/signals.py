# HU-037: Captura cada inicio de sesión exitoso y lo registra en LogInicioSesion.
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


def _get_client_ip(request):
    """Devuelve la IP del cliente, considerando proxies."""
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


@receiver(user_logged_in)
def registrar_inicio_sesion(sender, request, user, **kwargs):
    """Se ejecuta automáticamente después de cada login exitoso."""
    from .models import LogInicioSesion
    LogInicioSesion.objects.create(
        usuario=user,
        ip=_get_client_ip(request),
    )
