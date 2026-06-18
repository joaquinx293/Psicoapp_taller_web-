from django.db import models
from django.conf import settings


class TerminosCondiciones(models.Model):

    ROL_PACIENTE = 'paciente'
    ROL_ESPECIALISTA = 'especialista'
    ROL_CHOICES = [
        (ROL_PACIENTE, 'Paciente'),
        (ROL_ESPECIALISTA, 'Especialista'),
    ]

    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default=ROL_PACIENTE,
    )
    version = models.IntegerField()
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    vigente = models.BooleanField(default=True)

    class Meta:
        ordering = ['-version']
        unique_together = [('rol', 'version')]
        verbose_name = 'Términos y Condiciones'
        verbose_name_plural = 'Términos y Condiciones'

    def __str__(self):
        return f"[{self.get_rol_display()}] Versión {self.version} ({'Vigente' if self.vigente else 'Antigua'})"

    @classmethod
    def get_vigente(cls, rol=None):
        qs = cls.objects.filter(vigente=True)
        if rol:
            qs = qs.filter(rol=rol)
        return qs.order_by('-version').first()