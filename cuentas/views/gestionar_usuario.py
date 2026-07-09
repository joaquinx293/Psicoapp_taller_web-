# Acciones del administrador sobre cuentas de pacientes y especialistas
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Usuario


def _solo_admin(request):
    return request.user.is_authenticated and (
        request.user.es_admin() or request.user.is_superuser
    )


@login_required
def desactivar_usuario(request, pk):
    if not _solo_admin(request):
        return redirect('cuentas:login')
    if request.method != 'POST':
        return redirect('cuentas:dashboard_admin')

    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario.pk == request.user.pk:
        messages.error(request, 'No puedes desactivar tu propia cuenta.')
        return redirect('cuentas:dashboard_admin')

    usuario.estado = Usuario.INACTIVO
    usuario.is_active = False
    usuario.save()
    messages.warning(
        request,
        f'La cuenta de {usuario.get_full_name() or usuario.username} fue desactivada.'
    )
    return redirect('cuentas:dashboard_admin')


@login_required
def reactivar_usuario(request, pk):
    if not _solo_admin(request):
        return redirect('cuentas:login')
    if request.method != 'POST':
        return redirect('cuentas:dashboard_admin')

    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.estado = Usuario.ACTIVO
    usuario.is_active = True
    usuario.save()
    messages.success(
        request,
        f'La cuenta de {usuario.get_full_name() or usuario.username} fue reactivada.'
    )
    return redirect('cuentas:dashboard_admin')


@login_required
def eliminar_usuario(request, pk):
    if not _solo_admin(request):
        return redirect('cuentas:login')
    if request.method != 'POST':
        return redirect('cuentas:dashboard_admin')

    usuario = get_object_or_404(Usuario, pk=pk)

    # Bloquear auto-eliminación
    if usuario.pk == request.user.pk:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('cuentas:dashboard_admin')

    # Bloquear si es el último administrador
    if usuario.es_admin() or usuario.is_superuser:
        admins_activos = Usuario.objects.filter(
            rol=Usuario.ROL_ADMIN, is_active=True
        ).count()
        superusers = Usuario.objects.filter(is_superuser=True, is_active=True).count()
        if (admins_activos + superusers) <= 1:
            messages.error(
                request,
                'No se puede eliminar al único administrador del sistema.'
            )
            return redirect('cuentas:dashboard_admin')

    # Especialistas: baja lógica, nunca eliminar físicamente
    if usuario.es_especialista():
        nombre = usuario.get_full_name() or usuario.username
        usuario.estado = Usuario.INACTIVO
        usuario.is_active = False
        usuario.save()
        messages.warning(
            request,
            f'El especialista {nombre} fue desactivado del sistema '
            f'(no se eliminan sus registros clínicos).'
        )
        return redirect('cuentas:dashboard_admin')

    # Pacientes y admins: eliminación física (FKs son SET_NULL, datos clínicos se conservan)
    nombre = usuario.get_full_name() or usuario.username
    usuario.delete()
    messages.success(request, f'La cuenta de {nombre} fue eliminada permanentemente.')
    return redirect('cuentas:dashboard_admin')
