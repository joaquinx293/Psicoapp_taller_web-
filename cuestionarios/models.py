from django.db import models
from django.conf import settings


class Cuestionario(models.Model):
    BORRADOR = 'borrador'
    EN_REVISION = 'en_revision'
    APROBADO = 'aprobado'
    RECHAZADO = 'rechazado'

    ESTADOS = [
        (BORRADOR, 'Borrador'),
        (EN_REVISION, 'En revisión'),
        (APROBADO, 'Aprobado'),
        (RECHAZADO, 'Rechazado'),
    ]

    SUBTIPO_PERSONALIZADO = 'personalizado'
    SUBTIPO_GAD7 = 'gad7'
    SUBTIPOS = [
        (SUBTIPO_PERSONALIZADO, 'Personalizado'),
        (SUBTIPO_GAD7, 'GAD-7 (Ansiedad)'),
    ]

    especialista = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cuestionarios'
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=BORRADOR)
    subtipo = models.CharField(max_length=20, choices=SUBTIPOS, default=SUBTIPO_PERSONALIZADO)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def cantidad_preguntas_activas(self):
        return self.preguntas.filter(activa=True).count()

    def puede_enviar_revision(self):
        return self.estado in (self.BORRADOR, self.RECHAZADO)

    def __str__(self):
        return f"{self.nombre} ({self.get_estado_display()})"


class Pregunta(models.Model):
    ESCALA_LIKERT_4 = 'likert4'
    ESCALA_LIKERT_5 = 'likert5'
    ESCALA_SINO = 'sino'
    ESCALA_GAD7 = 'gad7'

    ESCALAS = [
        (ESCALA_LIKERT_4, 'Likert 0 a 3 (Nunca → Siempre)'),
        (ESCALA_LIKERT_5, 'Likert 0 a 4 (Nunca → Casi siempre)'),
        (ESCALA_SINO, 'Sí / No'),
        (ESCALA_GAD7, 'GAD-7 (Nunca → Casi cada día)'),
    ]

    cuestionario = models.ForeignKey(
        Cuestionario,
        on_delete=models.CASCADE,
        related_name='preguntas'
    )
    texto = models.CharField(max_length=250)
    escala = models.CharField(max_length=20, choices=ESCALAS, default=ESCALA_LIKERT_4)
    peso = models.IntegerField(default=1)
    orden = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['orden', 'id']

    def __str__(self):
        return self.texto[:50]


class AsignacionCuestionario(models.Model):
    """El especialista elige qué cuestionarios ve cada paciente."""
    especialista = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='asignaciones_dadas'
    )
    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cuestionarios_asignados'
    )
    cuestionario = models.ForeignKey(
        Cuestionario,
        on_delete=models.CASCADE,
        related_name='asignaciones'
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    class Meta:
        unique_together = [('paciente', 'cuestionario')]

    def __str__(self):
        return f"{self.cuestionario.nombre} → {self.paciente.username}"


class RespuestaCuestionario(models.Model):
    """Una sesión de respuesta de un paciente a un cuestionario."""
    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='respuestas'
    )
    cuestionario = models.ForeignKey(
        Cuestionario,
        on_delete=models.CASCADE,
        related_name='respuestas'
    )
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_respuesta']

    def puntaje_total(self):
        return sum(
            r.valor * r.pregunta.peso
            for r in self.respuestas_preguntas.all()
        )

    def clasificacion_gad7(self):
        """Retorna (etiqueta, color_bootstrap) según puntaje GAD-7."""
        puntaje = self.puntaje_total()
        if puntaje <= 4:
            return ('Mínimo (0-4)', 'success')
        elif puntaje <= 9:
            return ('Leve (5-9)', 'warning')
        elif puntaje <= 14:
            return ('Moderado (10-14)', 'danger')
        else:
            return ('Severo (15-21)', 'dark')

    def __str__(self):
        return f"{self.paciente.username} — {self.cuestionario.nombre} ({self.fecha_respuesta:%d/%m/%Y})"


class AsignacionPendiente(models.Model):
    """Cuestionarios pre-asignados a un paciente que aún no se ha registrado."""
    especialista = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='asignaciones_pendientes_dadas'
    )
    invitacion = models.ForeignKey(
        'gestion_usuarios.InvitacionPaciente',
        on_delete=models.CASCADE,
        related_name='asignaciones_pendientes'
    )
    cuestionario = models.ForeignKey(
        Cuestionario,
        on_delete=models.CASCADE,
        related_name='asignaciones_pendientes'
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('invitacion', 'cuestionario')]

    def __str__(self):
        return f"{self.cuestionario.nombre} -> {self.invitacion.correo_paciente} (pendiente)"


class RespuestaPregunta(models.Model):
    """Respuesta individual a una pregunta."""
    respuesta_cuestionario = models.ForeignKey(
        RespuestaCuestionario,
        on_delete=models.CASCADE,
        related_name='respuestas_preguntas'
    )
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE
    )
    valor = models.IntegerField()

    def __str__(self):
        return f"P{self.pregunta.pk}: {self.valor}"
