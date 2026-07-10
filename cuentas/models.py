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
        on_delete=models.SET_NULL,
        null=True, blank=True,
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
        nombre = self.paciente.username if self.paciente else '(anónimo)'
        return f"{nombre} – {self.fecha}: {self.valor}/10"


class PreguntaDiaria(models.Model):
    """HU-025: Pregunta diaria de seguimiento configurada por el especialista para un paciente."""
    paciente = models.OneToOneField(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pregunta_diaria',
        limit_choices_to={'rol': 'paciente'},
    )
    especialista = models.ForeignKey(
        'Usuario',
        on_delete=models.PROTECT,
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
        nombre = self.paciente.username if self.paciente else '(anónimo)'
        return f"[{estado}] {nombre}: {self.texto[:50]}"


class RespuestaPreguntaDiaria(models.Model):
    """HU-026: Respuesta del paciente a su pregunta diaria."""
    pregunta_diaria = models.ForeignKey(
        'PreguntaDiaria',
        on_delete=models.CASCADE,
        related_name='respuestas',
    )
    paciente = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
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
        nombre = self.paciente.username if self.paciente else '(anónimo)'
        return f"{nombre} – {self.fecha}"


class RecordatorioEmail(models.Model):
    """HU-027: Recordatorio diario por correo para registrar estado de ánimo."""
    paciente = models.OneToOneField(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
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
        nombre = self.paciente.username if self.paciente else '(anónimo)'
        return f"[{estado}] {nombre} a las {self.hora}"


class PistaMusical(models.Model):
    """HU-029: Pistas de música ambiental gestionadas por el administrador."""
    titulo  = models.CharField(max_length=100, unique=True, verbose_name='Título')
    archivo = models.FileField(upload_to='musica/', verbose_name='Archivo de audio')
    orden   = models.PositiveIntegerField(default=0, verbose_name='Orden')
    activa  = models.BooleanField(default=True, verbose_name='Activa')

    class Meta:
        ordering = ['orden', 'id']
        verbose_name = 'Pista musical'
        verbose_name_plural = 'Pistas musicales'

    def __str__(self):
        estado = '✓' if self.activa else '✗'
        return f"[{estado}] {self.titulo}"


class DatoDelDia(models.Model):
    """HU-032: Dato educativo diario gestionado por el administrador."""
    texto            = models.TextField(unique=True, verbose_name='Texto')
    fuente           = models.CharField(max_length=200, verbose_name='Fuente')
    activo           = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion   = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Dato del día'
        verbose_name_plural = 'Datos del día'

    @staticmethod
    def contar_palabras(texto):
        return len(texto.split())

    @classmethod
    def dato_de_hoy(cls):
        """Retorna el dato activo correspondiente a hoy (rotativo, sin repetición por día)."""
        from django.utils import timezone
        activos = list(cls.objects.filter(activo=True).order_by('id'))
        if not activos:
            return None
        dia = timezone.localdate().timetuple().tm_yday  # 1–366
        return activos[(dia - 1) % len(activos)]

    def __str__(self):
        estado = '✓' if self.activo else '✗'
        return f"[{estado}] {self.texto[:60]}... ({self.fuente})"


class DatoFavorito(models.Model):
    """HU-030: Dato del día marcado como favorito por el paciente."""
    paciente = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='datos_favoritos',
        limit_choices_to={'rol': 'paciente'},
    )
    dato = models.ForeignKey(
        'DatoDelDia',
        on_delete=models.CASCADE,
        related_name='guardado_por',
    )
    fecha_guardado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('paciente', 'dato')
        ordering = ['-fecha_guardado']
        verbose_name = 'Dato favorito'
        verbose_name_plural = 'Datos favoritos'

    def __str__(self):
        return f"{self.paciente.username} ❤ {self.dato.texto[:40]}"


class LogCambioMusica(models.Model):
    """HU-033: Auditoría de cambios en las pistas de música ambiental."""

    ACCION_SUBIR       = 'subir'
    ACCION_ELIMINAR    = 'eliminar'
    ACCION_ACTIVAR     = 'activar'
    ACCION_DESACTIVAR  = 'desactivar'
    ACCION_REORDENAR   = 'reordenar'

    ACCIONES = [
        (ACCION_SUBIR,      'Pista subida'),
        (ACCION_ELIMINAR,   'Pista eliminada'),
        (ACCION_ACTIVAR,    'Pista activada'),
        (ACCION_DESACTIVAR, 'Pista desactivada'),
        (ACCION_REORDENAR,  'Orden modificado'),
    ]

    admin        = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='logs_musica',
        verbose_name='Administrador',
    )
    accion       = models.CharField(max_length=20, choices=ACCIONES)
    pista_titulo = models.CharField(max_length=100, verbose_name='Pista')
    detalle      = models.CharField(max_length=200, blank=True, verbose_name='Detalle')
    fecha        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Log de música'
        verbose_name_plural = 'Logs de música'

    def __str__(self):
        admin = self.admin.username if self.admin else '(eliminado)'
        return f"{self.fecha:%d/%m/%Y %H:%M} — {admin}: {self.get_accion_display()} → {self.pista_titulo}"


class PreferenciasVisibilidad(models.Model):
    """Permisos que el especialista configura para controlar qué ve el paciente."""
    paciente = models.OneToOneField(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='preferencias_visibilidad',
        limit_choices_to={'rol': 'paciente'},
    )
    ver_historial_animo_habilitado = models.BooleanField(
        default=True,
        verbose_name='Ver historial de ánimo',
    )
    ver_calendario_habilitado = models.BooleanField(
        default=True,
        verbose_name='Ver calendario emocional',
    )
    ver_promedio_animo_habilitado = models.BooleanField(
        default=True,
        verbose_name='Ver promedio de ánimo',
    )
    editar_datos_habilitado = models.BooleanField(
        default=True,
        verbose_name='Editar datos personales',
        help_text='Permite al paciente cambiar su nombre y correo.',
    )
    cambiar_contrasena_habilitado = models.BooleanField(
        default=True,
        verbose_name='Cambiar contraseña',
        help_text='Permite al paciente actualizar su contraseña.',
    )
    configurar_recordatorio_habilitado = models.BooleanField(
        default=True,
        verbose_name='Configurar recordatorio por correo',
        help_text='Permite al paciente activar o cambiar la hora del recordatorio.',
    )

    class Meta:
        verbose_name = 'Preferencias de visibilidad'
        verbose_name_plural = 'Preferencias de visibilidad'

    def __str__(self):
        return f"Visibilidad de {self.paciente.username}"


class LogInicioSesion(models.Model):
    """HU-037: Registro automático de cada inicio de sesión exitoso."""
    usuario = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='logs_sesion',
    )
    fecha = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Log de inicio de sesión'
        verbose_name_plural = 'Logs de inicio de sesión'

    def __str__(self):
        nombre = self.usuario.username if self.usuario else '(eliminado)'
        return f"{nombre} – {self.fecha:%d/%m/%Y %H:%M}"


class LogBienestar(models.Model):
    """HU-038: Registro de acceso y uso de herramientas de bienestar."""

    RESPIRACION = 'respiracion'
    MUSICA      = 'musica'
    DATO_DIA    = 'dato_dia'

    HERRAMIENTAS = [
        (RESPIRACION, 'Respiración guiada'),
        (MUSICA,      'Música ambiental'),
        (DATO_DIA,    'Dato del día / Favoritos'),
    ]

    usuario = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='logs_bienestar',
    )
    herramienta       = models.CharField(max_length=20, choices=HERRAMIENTAS)
    fecha             = models.DateTimeField(auto_now_add=True)
    duracion_segundos = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Solo para respiración: segundos de sesión completada.',
    )

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Log de bienestar'
        verbose_name_plural = 'Logs de bienestar'

    def __str__(self):
        nombre = self.usuario.username if self.usuario else '(anónimo)'
        dur    = f' ({self.duracion_segundos}s)' if self.duracion_segundos else ''
        return f"{nombre} — {self.get_herramienta_display()}{dur} · {self.fecha:%d/%m/%Y %H:%M}"


class Notificacion(models.Model):
    """HU-010: Notificaciones in-app. Incluye solicitudes de baja de pacientes y especialistas."""

    # Tipos
    TIPO_GENERAL = 'general'
    TIPO_BAJA_PACIENTE = 'solicitud_baja_paciente'
    TIPO_BAJA_ESPECIALISTA = 'solicitud_baja_especialista'

    TIPOS = [
        (TIPO_GENERAL, 'General'),
        (TIPO_BAJA_PACIENTE, 'Solicitud de baja (paciente)'),
        (TIPO_BAJA_ESPECIALISTA, 'Solicitud de baja (especialista)'),
    ]

    destinatario = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='notificaciones',
    )
    solicitante = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='notificaciones_enviadas',
    )
    tipo = models.CharField(max_length=30, choices=TIPOS, default=TIPO_GENERAL)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        dest = self.destinatario.username if self.destinatario else '(eliminado)'
        return f"→ {dest}: {self.mensaje[:50]}"
