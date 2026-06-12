# HU-008: Listar pacientes asignados
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from ..models import InvitacionPaciente


@login_required
def dashboard(request):
    """Página de inicio del especialista."""
    if not request.user.es_especialista():
        return redirect('cuentas:login')
    return render(request, 'gestion_usuarios/dashboard.html')


@login_required
def listado_pacientes(request):
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    invitaciones = InvitacionPaciente.objects.filter(
        especialista=request.user
    ).order_by('-fecha_creacion')

    return render(request, 'gestion_usuarios/listado_pacientes.html', {
        'invitaciones': invitaciones
    })
