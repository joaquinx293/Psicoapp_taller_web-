# HU-016: El administrador valida cuestionarios enviados por especialistas
from django.contrib import admin, messages
from .models import Cuestionario, Pregunta, AsignacionCuestionario, RespuestaCuestionario


class PreguntaInline(admin.TabularInline):
    model = Pregunta
    extra = 0
    fields = ['texto', 'escala', 'peso', 'orden', 'activa']
    # El admin puede editar y eliminar preguntas directamente


@admin.register(Cuestionario)
class CuestionarioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'especialista', 'estado', 'cantidad_preguntas_activas', 'fecha_creacion']
    list_filter = ['estado']
    search_fields = ['nombre', 'especialista__username']
    readonly_fields = ['especialista', 'nombre', 'descripcion', 'fecha_creacion']
    inlines = [PreguntaInline]
    actions = ['aprobar_cuestionarios', 'rechazar_cuestionarios']

    @admin.action(description='Aprobar cuestionarios seleccionados')
    def aprobar_cuestionarios(self, request, queryset):
        actualizados = queryset.filter(estado=Cuestionario.EN_REVISION).update(
            estado=Cuestionario.APROBADO
        )
        self.message_user(
            request,
            f'{actualizados} cuestionario(s) aprobado(s). Ya visibles para todos los especialistas.',
            messages.SUCCESS
        )

    @admin.action(description='Rechazar cuestionarios seleccionados')
    def rechazar_cuestionarios(self, request, queryset):
        actualizados = queryset.filter(estado=Cuestionario.EN_REVISION).update(
            estado=Cuestionario.RECHAZADO
        )
        self.message_user(
            request,
            f'{actualizados} cuestionario(s) rechazado(s). El especialista puede corregirlos.',
            messages.WARNING
        )


@admin.register(AsignacionCuestionario)
class AsignacionCuestionarioAdmin(admin.ModelAdmin):
    list_display = ['cuestionario', 'paciente', 'especialista', 'activa', 'fecha_asignacion']
    list_filter = ['activa']
    search_fields = ['cuestionario__nombre', 'paciente__username', 'especialista__username']


@admin.register(RespuestaCuestionario)
class RespuestaCuestionarioAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'cuestionario', 'fecha_respuesta', 'puntaje_total']
    list_filter = ['cuestionario']
    search_fields = ['paciente__username', 'cuestionario__nombre']
    readonly_fields = ['paciente', 'cuestionario', 'fecha_respuesta']
