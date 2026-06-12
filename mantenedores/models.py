from django.db import models
from django.conf import settings


class TerminosCondiciones(models.Model):

    version = models.IntegerField(unique=True)
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
        verbose_name = 'Terminos y Condiciones'
        verbose_name_plural = 'Terminos y Condiciones'

    def __str__(self):
        return f"Version {self.version} ({'Vigente' if self.vigente else 'Antigua'})"

    @classmethod
    def get_vigente(cls):
        return cls.objects.filter(vigente=True).order_by('-version').first()