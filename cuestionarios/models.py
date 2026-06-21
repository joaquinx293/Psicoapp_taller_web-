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
    SUBTIPO_PSS10 = 'pss10'
    SUBTIPO_PHQ9 = 'phq9'
    SUBTIPOS = [
        (SUBTIPO_PERSONALIZADO, 'Personalizado'),
        (SUBTIPO_GAD7, 'GAD-7 (Ansiedad)'),
        (SUBTIPO_PSS10, 'PSS-10 (Estrés percibido)'),
        (SUBTIPO_PHQ9, 'PHQ-9 (Depresión)'),
    ]
    especialista = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cuestionarios'
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=BORRADOR)
    subtipo = models.CharField(max_length=20, choices=SUBTIPOS, default=SUBTIPO_PERSONALIZADO)
    publico = models.BooleanField(
        default=False,
        help_text='Si está activo, todos los especialistas pueden verlo y copiarlo.'
    )
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
    ESCALA_PSS10 = 'pss10'
    ESCALA_PHQ9 = 'phq9'
    ESCALA_TEXTO = 'texto'
    ESCALA_BINARIO = 'binario'
    ESCALA_FECHA = 'fecha'
    ESCALA_VF = 'verdadero_falso'
    ESCALAS = [
        (ESCALA_LIKERT_4, 'Likert 0 a 3 (Nunca → Siempre)'),
        (ESCALA_LIKERT_5, 'Likert 0 a 4 (Nunca → Casi siempre)'),
        (ESCALA_SINO, 'Sí / No'),
        (ESCALA_GAD7, 'GAD-7 (Nunca → Casi cada día)'),
        (ESCALA_PSS10, 'PSS-10 (Nunca → Muy a menudo)'),
        (ESCALA_PHQ9, 'PHQ-9 (Ningún día → Casi todos los días)'),
        (ESCALA_TEXTO, 'Caja de texto (sin puntaje)'),
        (ESCALA_BINARIO, 'Etiquetas personalizadas (ej: Triste / Feliz)'),
        (ESCALA_FECHA, 'Fecha y hora (sin puntaje)'),
        (ESCALA_VF, 'Verdadero / Falso'),
    ]
    ESCALAS_SIN_PUNTAJE = {ESCALA_TEXTO, ESCALA_FECHA}
    ESCALAS_VALOR_TEXTO = {ESCALA_TEXTO, ESCALA_FECHA}
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
    etiqueta_opcion_1 = models.CharField(max_length=100, blank=True, default='')
    etiqueta_opcion_2 = models.CharField(max_length=100, blank=True, default='')
    # esto es para el cuestionario  PSS-10 
    invertir = models.BooleanField(
        default=False,
        help_text='Si está activo, el valor se invierte (4 - valor) antes de calcular el puntaje.'
    )
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
        total = 0
        for r in self.respuestas_preguntas.all():
            if r.valor is None:
                continue
            if r.pregunta.escala in Pregunta.ESCALAS_SIN_PUNTAJE:
                continue
            valor = (4 - r.valor) if r.pregunta.invertir else r.valor
            total += valor * r.pregunta.peso
        return total

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

    def clasificacion_pss10(self):
        """Retorna (etiqueta, color_bootstrap) según puntaje PSS-10."""
        puntaje = self.puntaje_total()
        if puntaje <= 13:
            return ('Estrés bajo (0-13)', 'success')
        elif puntaje <= 26:
            return ('Estrés moderado (14-26)', 'warning')
        else:
            return ('Estrés alto (27-40)', 'danger')

    def clasificacion_phq9(self):
        """Retorna (etiqueta, color_bootstrap) según puntaje PHQ-9."""
        puntaje = self.puntaje_total()
        if puntaje <= 4:
            return ('Mínimo (0-4)', 'success')
        elif puntaje <= 9:
            return ('Leve (5-9)', 'warning')
        elif puntaje <= 14:
            return ('Moderado (10-14)', 'danger')
        else:
            return ('Severo (15-27)', 'dark')

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
    valor = models.IntegerField(null=True, blank=True)
    valor_texto = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"P{self.pregunta.pk}: {self.valor if self.valor is not None else self.valor_texto}"
