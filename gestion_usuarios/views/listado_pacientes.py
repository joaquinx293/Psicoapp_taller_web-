# HU-008: Listar pacientes asignados
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect

from ..models import InvitacionPaciente
from cuentas.models import Notificacion


@login_required
def dashboard(request):
    """Página de inicio del especialista."""
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    # HU-010: notificaciones no leídas (se marcan leídas al abrir el dashboard)
    notificaciones = list(Notificacion.objects.filter(
        destinatario=request.user, leida=False
    ))
    Notificacion.objects.filter(
        destinatario=request.user, leida=False
    ).update(leida=True)

    return render(request, 'gestion_usuarios/dashboard.html', {
        'notificaciones': notificaciones,
    })


@login_required
def listado_pacientes(request):
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    q = request.GET.get('q', '').strip()

    invitaciones = InvitacionPaciente.objects.filter(
        especialista=request.user
    ).order_by('-fecha_creacion')

    if q:
        invitaciones = invitaciones.filter(
            Q(nombre_paciente__icontains=q) | Q(correo_paciente__icontains=q)
        )

    paginator = Paginator(invitaciones, 20)
    page_obj  = paginator.get_page(request.GET.get('page'))

    return render(request, 'gestion_usuarios/listado_pacientes.html', {
        'page_obj': page_obj,
        'q':        q,
    })
