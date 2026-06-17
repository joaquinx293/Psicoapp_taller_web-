from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from .forms import RegistroEspecialistaForm
from .models import Usuario
from mantenedores.models import TerminosCondiciones


def registro_especialista(request):
    terminos = TerminosCondiciones.get_vigente()

    if request.method == 'POST':
        form = RegistroEspecialistaForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.rol = Usuario.ROL_ESPECIALISTA
            usuario.estado = Usuario.PENDIENTE
            usuario.is_active = False

            if terminos:
                usuario.terminos_aceptados_version = terminos.version
                usuario.terminos_aceptados_fecha = timezone.now()

            usuario.save()

            send_mail(
                'Solicitud de registro recibida - PsicoApp',
                f'Hola {usuario.first_name}, recibimos tu solicitud. '
                f'Te avisaremos cuando sea aprobada.',
                'noreply@psicoapp.cl',
                [usuario.email],
                fail_silently=True,
            )

            messages.success(
                request,
                'Solicitud enviada correctamente. '
                'Recibirás un correo cuando sea aprobada.'
            )
            return redirect('cuentas:login')
    else:
        form = RegistroEspecialistaForm()

    return render(request, 'cuentas/registro_especialista.html', {
        'form': form,
        'terminos': terminos,
    })


@login_required
def redireccion_por_rol(request):
    if request.user.es_admin() or request.user.is_superuser:
        return redirect('/admin/')
    elif request.user.es_especialista():
        return redirect('gestion_usuarios:dashboard')
    else:
        return redirect('cuentas:perfil_paciente')


@login_required
def perfil_paciente(request):
    return render(request, 'cuentas/perfil_paciente.html')