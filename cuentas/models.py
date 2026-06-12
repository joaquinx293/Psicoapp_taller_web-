from django.db import models
from django.contrib.auth.models import AbstractUser


class Especialidad(models.Model):
    """Categorías de especialidad gestionadas por el administrador."""
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):

    # Roles
    ROL_PACIENTE = 'paciente'
    ROL_ESPECIALISTA = 'especialista'
    ROL_ADMIN = 'admin'

    ROLES = [
        (ROL_PACIENTE, 'Paciente'),
        (ROL_ESPECIALISTA, 'Especialista'),
        (ROL_ADMIN, 'Administrador'),
    ]

    # Estados
    PENDIENTE = 'pendiente'
    ACTIVO = 'activo'
    RECHAZADO = 'rechazado'
    INACTIVO = 'inactivo'

    ESTADOS = [
        (PENDIENTE, 'Pendiente de validacion'),
        (ACTIVO, 'Activo'),
        (RECHAZADO, 'Rechazado'),
        (INACTIVO, 'Inactivo'),
    ]

    rol = models.CharField(
        max_length=20, choices=ROLES, default=ROL_PACIENTE
    )
    estado = models.CharField(
        max_length=20, choices=ESTADOS, default=ACTIVO
    )
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='especialistas',
        verbose_name='Especialidad',
    )
    terminos_aceptados_fecha = models.DateTimeField(
        null=True, blank=True
    )
    fecha_nacimiento = models.DateField(null=True, blank=True)
    motivo_rechazo = models.TextField(null=True, blank=True)

    def es_paciente(self):
        return self.rol == self.ROL_PACIENTE

    def es_especialista(self):
        return self.rol == self.ROL_ESPECIALISTA

    def es_admin(self):
        return self.rol == self.ROL_ADMIN

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
