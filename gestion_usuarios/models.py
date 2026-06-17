import random
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


def generar_pin():
    """Genera un PIN numérico de 6 dígitos."""
    return str(random.randint(100000, 999999))


class InvitacionPaciente(models.Model):

    PENDIENTE = 'pendiente'
    ACEPTADA = 'aceptada'
    EXPIRADA = 'expirada'
    ESTADOS = [
        (PENDIENTE, 'Pendiente'),
        (ACEPTADA, 'Aceptada'),
        (EXPIRADA, 'Expirada'),
    ]
    especialista = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invitaciones_enviadas'
    )
    nombre_paciente = models.CharField(max_length=150)
    correo_paciente = models.EmailField()
    pin = models.CharField(max_length=6, editable=False, default=generar_pin)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=PENDIENTE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    paciente = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='invitacion_recibida'
    )
    def esta_vigente(self):
        limite = self.fecha_creacion + timedelta(hours=24)
        return self.estado == self.PENDIENTE and timezone.now() <= limite
    def __str__(self):
        return f"Invitación a {self.correo_paciente} ({self.estado})"
