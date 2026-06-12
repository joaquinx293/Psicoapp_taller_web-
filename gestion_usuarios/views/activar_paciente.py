# HU-003: Activar cuenta como paciente mediante PIN
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

from ..models import InvitacionPaciente
from ..forms import IngresarPinForm, ActivarPacienteForm
from cuentas.models import Usuario
from mantenedores.models import TerminosCondiciones


def ingresar_pin(request):
    """Paso 1: el paciente ingresa su correo y el PIN recibido."""
    if request.method == 'POST':
        form = IngresarPinForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            pin = form.cleaned_data['pin']

            try:
                invitacion = InvitacionPaciente.objects.get(
                    correo_paciente=correo,
                    pin=pin,
                    estado=InvitacionPaciente.PENDIENTE,
                )
            except InvitacionPaciente.DoesNotExist:
                form.add_error(None, 'Correo o codigo incorrecto.')
                return render(request, 'gestion_usuarios/ingresar_pin.html', {'form': form})

            if not invitacion.esta_vigente():
                invitacion.estado = InvitacionPaciente.EXPIRADA
                invitacion.save()
                messages.error(request, 'Tu codigo ha expirado. Pide una nueva invitacion.')
                return render(request, 'gestion_usuarios/ingresar_pin.html', {'form': form})

            # Guardamos el id de la invitación en sesión para el paso 2
            request.session['invitacion_id'] = invitacion.pk
            return redirect('gestion_usuarios:completar_registro')
    else:
        form = IngresarPinForm()

    return render(request, 'gestion_usuarios/ingresar_pin.html', {'form': form})


def completar_registro(request):
    """Paso 2: el paciente elige usuario y contraseña."""
    invitacion_id = request.session.get('invitacion_id')
    if not invitacion_id:
        messages.error(request, 'Sesion expirada. Ingresa tu codigo nuevamente.')
        return redirect('gestion_usuarios:ingresar_pin')

    try:
        invitacion = InvitacionPaciente.objects.get(
            pk=invitacion_id,
            estado=InvitacionPaciente.PENDIENTE,
        )
    except InvitacionPaciente.DoesNotExist:
        messages.error(request, 'La invitacion ya no es valida.')
        return redirect('gestion_usuarios:ingresar_pin')

    if not invitacion.esta_vigente():
        invitacion.estado = InvitacionPaciente.EXPIRADA
        invitacion.save()
        messages.error(request, 'Tu codigo ha expirado. Pide una nueva invitacion.')
        return redirect('gestion_usuarios:ingresar_pin')

    terminos = TerminosCondiciones.get_vigente()

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
                paciente.terminos_aceptados_fecha = timezone.now()

            paciente.save()

            invitacion.paciente = paciente
            invitacion.estado = InvitacionPaciente.ACEPTADA
            invitacion.save()

            # Limpiar sesión
            del request.session['invitacion_id']

            messages.success(
                request,
                'Cuenta activada correctamente. Ya puedes iniciar sesion.'
            )
            return redirect('cuentas:login')
    else:
        form = ActivarPacienteForm()

    return render(request, 'gestion_usuarios/completar_registro.html', {
        'form': form,
        'invitacion': invitacion,
        'terminos': terminos,
    })
