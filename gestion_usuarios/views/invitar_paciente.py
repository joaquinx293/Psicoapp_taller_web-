# HU-007: Invitar paciente por correo
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

from ..models import InvitacionPaciente
from ..forms import InvitarPacienteForm


@login_required
def invitar_paciente(request):
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    if request.method == 'POST':
        form = InvitarPacienteForm(request.POST)
        if form.is_valid():
            invitacion = form.save(commit=False)
            invitacion.especialista = request.user
            invitacion.save()  # el PIN se genera automáticamente en save()

            send_mail(
                'Invitacion a PsicoApp',
                f'Hola {invitacion.nombre_paciente},\n\n'
                f'{request.user.get_full_name() or request.user.username} '
                f'te ha invitado a PsicoApp.\n\n'
                f'Tu codigo de activacion es:\n\n'
                f'    {invitacion.pin}\n\n'
                f'Ingresa a PsicoApp, ve a la seccion "Fui invitado" '
                f'e introduce tu correo y este codigo.\n\n'
                f'Este codigo es valido por 24 horas.\n\n'
                f'Saludos, equipo PsicoApp.',
                'noreply@psicoapp.cl',
                [invitacion.correo_paciente],
                fail_silently=True,
            )

            messages.success(
                request,
                f'Invitacion enviada a {invitacion.correo_paciente}. '
                f'PIN de activacion: {invitacion.pin}'
            )
            return redirect('gestion_usuarios:listado_pacientes')
    else:
        form = InvitarPacienteForm()

    return render(request, 'gestion_usuarios/invitar_paciente.html', {
        'form': form
    })
