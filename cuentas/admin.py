from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.shortcuts import render

from .models import Especialidad, Usuario


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    """El administrador crea y elimina las categorías de especialidad."""
    list_display = ['nombre']
    search_fields = ['nombre']


class MotivoRechazoForm(forms.Form):
    motivo = forms.CharField(
        label='Motivo del rechazo',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
    )


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):

    list_display = ['username', 'email', 'first_name', 'last_name',
                    'rol', 'estado', 'is_active']
    list_filter = ['rol', 'estado']
    actions = ['aprobar_especialistas', 'rechazar_especialistas']

    fieldsets = UserAdmin.fieldsets + (
        ('Información PsicoApp', {
            'fields': ('rol', 'estado', 'especialidad',
                       'fecha_nacimiento', 'motivo_rechazo',
                       'terminos_aceptados_fecha')
        }),
    )

    @admin.action(description='Aprobar especialistas seleccionados')
    def aprobar_especialistas(self, request, queryset):
        aprobados = 0
        for usuario in queryset.filter(
            rol=Usuario.ROL_ESPECIALISTA,
            estado=Usuario.PENDIENTE
        ):
            usuario.estado = Usuario.ACTIVO
            usuario.is_active = True
            usuario.save()
            send_mail(
                'Tu cuenta fue aprobada - PsicoApp',
                f'Hola {usuario.first_name}, tu solicitud fue aprobada. '
                f'Ya puedes iniciar sesión en PsicoApp.',
                'noreply@psicoapp.cl',
                [usuario.email],
                fail_silently=True,
            )
            aprobados += 1
        self.message_user(request, f'{aprobados} especialista(s) aprobado(s).', messages.SUCCESS)

    @admin.action(description='Rechazar solicitudes seleccionadas')
    def rechazar_especialistas(self, request, queryset):
        pendientes = queryset.filter(estado=Usuario.PENDIENTE)

        if 'aplicar' in request.POST:
            form = MotivoRechazoForm(request.POST)
            if form.is_valid():
                motivo = form.cleaned_data['motivo']
                rechazados = 0
                for usuario in pendientes:
                    usuario.estado = Usuario.RECHAZADO
                    usuario.motivo_rechazo = motivo
                    usuario.save()
                    send_mail(
                        'Solicitud rechazada - PsicoApp',
                        f'Hola {usuario.first_name}, tu solicitud no fue aprobada.\n\n'
                        f'Motivo: {motivo}',
                        'noreply@psicoapp.cl',
                        [usuario.email],
                        fail_silently=True,
                    )
                    rechazados += 1
                self.message_user(
                    request, f'{rechazados} solicitud(es) rechazada(s).', messages.SUCCESS
                )
                return None
        else:
            form = MotivoRechazoForm()

        return render(request, 'admin/rechazar_especialistas.html', {
            'especialistas': pendientes,
            'form': form,
        })
