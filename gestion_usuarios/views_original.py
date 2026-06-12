from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils import timezone
from .models import InvitacionPaciente
from .forms import InvitarPacienteForm, ActivarPacienteForm
from cuentas.models import Usuario
from mantenedores.models import TerminosCondiciones


@login_required
def dashboard(request):
    """Inicio del especialista"""
    if not request.user.es_especialista():
        return redirect('cuentas:login')
    return render(request, 'gestion_usuarios/dashboard.html')


@login_required
def invitar_paciente(request):
    """HU-007: invitar paciente por correo"""
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    if request.method == 'POST':
        form = InvitarPacienteForm(request.POST)
        if form.is_valid():
            invitacion = form.save(commit=False)
            invitacion.especialista = request.user
            invitacion.save()
            enlace = request.build_absolute_uri(
                f'/gestion/activar/{invitacion.token}/'
            )

            send_mail(
                'Invitacion a PsicoApp',
                f'Hola {invitacion.nombre_paciente},\n\n'
                f'{request.user.first_name} te ha invitado a PsicoApp. '
                f'Activa tu cuenta en el siguiente enlace (valido por 72 horas):\n\n'
                f'{enlace}\n\n'
                f'Saludos, equipo PsicoApp.',
                'noreply@psicoapp.cl',
                [invitacion.correo_paciente],
                fail_silently=True,
            )

            messages.success(
                request,
                f'Invitacion enviada a {invitacion.correo_paciente}.'
            )
            return redirect('gestion_usuarios:listado_pacientes')
    else:
        form = InvitarPacienteForm()

    return render(request, 'gestion_usuarios/invitar_paciente.html', {
        'form': form
    })


def activar_paciente(request, token):
    """HU-003: el paciente activa su cuenta desde el enlace"""
    invitacion = get_object_or_404(InvitacionPaciente, token=token)
    terminos = TerminosCondiciones.get_vigente()

    # Validar vigencia
    if not invitacion.esta_vigente():
        if invitacion.estado == InvitacionPaciente.PENDIENTE:
            invitacion.estado = InvitacionPaciente.EXPIRADA
            invitacion.save()
        return render(request, 'gestion_usuarios/enlace_invalido.html')

    if request.method == 'POST':
        form = ActivarPacienteForm(request.POST)
        if form.is_valid():
            paciente = Usuario(
                username=form.cleaned_data['username'],
                email=invitacion.correo_paciente,
                first_name=invitacion.nombre_paciente,
                rol=Usuario.ROL_PACIENTE,
                estado=Usuario.ACTIVO,
                is_active=True,
            )
            paciente.set_password(form.cleaned_data['password1'])

            if terminos:
                paciente.terminos_aceptados_version = terminos.version
                paciente.terminos_aceptados_fecha = timezone.now()

            paciente.save()

            # Vincular invitacion con el paciente creado
            invitacion.paciente = paciente
            invitacion.estado = InvitacionPaciente.ACEPTADA
            invitacion.save()

            messages.success(
                request,
                'Cuenta activada correctamente. Ya puedes iniciar sesion.'
            )
            return redirect('cuentas:login')
    else:
        form = ActivarPacienteForm()

    return render(request, 'gestion_usuarios/activar_paciente.html', {
        'form': form,
        'invitacion': invitacion,
        'terminos': terminos,
    })


@login_required
def listado_pacientes(request):
    """HU-008: el especialista ve sus pacientes"""
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    invitaciones = InvitacionPaciente.objects.filter(
        especialista=request.user
    ).order_by('-fecha_creacion')

    return render(request, 'gestion_usuarios/listado_pacientes.html', {
        'invitaciones': invitaciones
    })