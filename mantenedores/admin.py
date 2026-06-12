from django.contrib import admin
from .models import TerminosCondiciones


@admin.register(TerminosCondiciones)
class TerminosCondicionesAdmin(admin.ModelAdmin):

    list_display = ['version', 'fecha_publicacion', 'vigente', 'autor']
    list_filter = ['vigente']
    readonly_fields = ['version', 'fecha_publicacion', 'autor']

    def save_model(self, request, obj, form, change):
        if not change:
            ultima = TerminosCondiciones.objects.order_by('-version').first()
            obj.version = (ultima.version + 1) if ultima else 1
            obj.autor = request.user

            TerminosCondiciones.objects.update(vigente=False)
            obj.vigente = True
        super().save_model(request, obj, form, change)