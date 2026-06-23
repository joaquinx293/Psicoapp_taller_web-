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


class RegistroAnimo(models.Model):
    """HU-022: Registro diario del estado de ánimo del paciente (1–10)."""

    ETIQUETAS = {
        1: 'Muy mal',
        2: 'Muy mal',
        3: 'Mal',
        4: 'Mal',
        5: 'Regular',
        6: 'Regular',
        7: 'Bien',
        8: 'Bien',
        9: 'Excelente',
        10: 'Excelente',
    }

    paciente = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='registros_animo',
        limit_choices_to={'rol': 'paciente'},
    )
    fecha = models.DateField()
    valor = models.IntegerField()  # 1–10

    class Meta:
        unique_together = ('paciente', 'fecha')
        ordering = ['-fecha']
        verbose_name = 'Registro de ánimo'
        verbose_name_plural = 'Registros de ánimo'

    def get_etiqueta(self):
        return self.ETIQUETAS.get(self.valor, '')

    def __str__(self):
        return f"{self.paciente.username} – {self.fecha}: {self.valor}/10"


class PreguntaDiaria(models.Model):
    """HU-025: Pregunta diaria de seguimiento configurada por el especialista para un paciente."""
    paciente = models.OneToOneField(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='pregunta_diaria',
        limit_choices_to={'rol': 'paciente'},
    )
    especialista = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='preguntas_diarias_configuradas',
        limit_choices_to={'rol': 'especialista'},
    )
    texto = models.CharField(max_length=200)
    hora_inicio = models.TimeField(
        help_text='La pregunta se muestra al paciente a partir de esta hora.'
    )
    activa = models.BooleanField(default=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pregunta diaria'
        verbose_name_plural = 'Preguntas diarias'

    def __str__(self):
        estado = 'activa' if self.activa else 'inactiva'
        return f"[{estado}] {self.paciente.username}: {self.texto[:50]}"


class RespuestaPreguntaDiaria(models.Model):
    """HU-026: Respuesta del paciente a su pregunta diaria."""
    pregunta_diaria = models.ForeignKey(
        'PreguntaDiaria',
        on_delete=models.CASCADE,
        related_name='respuestas',
    )
    paciente = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='respuestas_pregunta_diaria',
    )
    fecha = models.DateField()
    texto = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('pregunta_diaria', 'fecha')
        ordering = ['-fecha']
        verbose_name = 'Respuesta pregunta diaria'
        verbose_name_plural = 'Respuestas pregunta diaria'

    def __str__(self):
        return f"{self.paciente.username} – {self.fecha}"


class RecordatorioEmail(models.Model):
    """HU-027: Recordatorio diario por correo para registrar estado de ánimo."""
    paciente = models.OneToOneField(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='recordatorio_email',
        limit_choices_to={'rol': 'paciente'},
    )
    activo = models.BooleanField(default=False)
    hora = models.TimeField(
        help_text='Hora a la que se envía el recordatorio.'
    )
    ultimo_envio = models.DateField(
        null=True, blank=True,
        help_text='Fecha del último envío para evitar duplicados.'
    )

    class Meta:
        verbose_name = 'Recordatorio por email'
        verbose_name_plural = 'Recordatorios por email'

    def __str__(self):
        estado = 'activo' if self.activo else 'inactivo'
        return f"[{estado}] {self.paciente.username} a las {self.hora}"


class Notificacion(models.Model):
    """HU-010: Notificaciones in-app para especialistas."""
    destinatario = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='notificaciones',
    )
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"→ {self.destinatario.username}: {self.mensaje[:50]}"
