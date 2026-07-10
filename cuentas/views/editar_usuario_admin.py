# Admin edita datos básicos de cualquier usuario (nombre, email, rol, estado, especialidad)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Especialidad, Usuario


@login_required
def editar_usuario_admin(request, pk):
    if not (request.user.es_admin() or request.user.is_superuser):
        return redirect('cuentas:redireccion')

    usuario = get_object_or_404(Usuario, pk=pk)
    errores = {}

    if request.method == 'POST':
        first_name     = request.POST.get('first_name', '').strip()
        last_name      = request.POST.get('last_name', '').strip()
        email          = request.POST.get('email', '').strip().lower()
        rol            = request.POST.get('rol', '').strip()
        estado         = request.POST.get('estado', '').strip()
        especialidad_pk = request.POST.get('especialidad', '').strip()

        # Validaciones
        if not email:
            errores['email'] = 'El correo es obligatorio.'
        elif Usuario.objects.filter(email=email).exclude(pk=pk).exists():
            errores['email'] = 'Ese correo ya está en uso por otro usuario.'

        roles_validos   = [r[0] for r in Usuario.ROLES]
        estados_validos = [e[0] for e in Usuario.ESTADOS]

        if rol not in roles_validos:
            errores['rol'] = 'Rol no válido.'
        if estado not in estados_validos:
            errores['estado'] = 'Estado no válido.'

        # Resolver especialidad (solo aplica si el usuario es especialista)
        especialidad_obj = None
        if rol == Usuario.ROL_ESPECIALISTA and especialidad_pk:
            try:
                especialidad_obj = Especialidad.objects.get(pk=int(especialidad_pk))
            except (Especialidad.DoesNotExist, ValueError):
                errores['especialidad'] = 'Especialidad no válida.'

        if not errores:
            usuario.first_name   = first_name
            usuario.last_name    = last_name
            usuario.email        = email
            usuario.rol          = rol
            usuario.estado       = estado
            usuario.is_active    = estado == Usuario.ACTIVO
            usuario.especialidad = especialidad_obj if rol == Usuario.ROL_ESPECIALISTA else None
            usuario.save(update_fields=[
                'first_name', 'last_name', 'email',
                'rol', 'estado', 'is_active', 'especialidad',
            ])
            messages.success(request, f'Usuario {usuario.username} actualizado correctamente.')
            return redirect('cuentas:dashboard_admin')

    return render(request, 'cuentas/editar_usuario_admin.html', {
        'usuario':       usuario,
        'errores':       errores,
        'roles':         Usuario.ROLES,
        'estados':       Usuario.ESTADOS,
        'especialidades': Especialidad.objects.all(),
    })
