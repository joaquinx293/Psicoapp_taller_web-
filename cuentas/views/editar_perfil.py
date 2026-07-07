# Cambio 4: Editar perfil del paciente
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required

from cuentas.models import Usuario, RecordatorioEmail, PreferenciasVisibilidad


def _get_prefs(usuario):
    try:
        return usuario.preferencias_visibilidad
    except PreferenciasVisibilidad.DoesNotExist:
        return None


@login_required
def editar_perfil_paciente(request):
    if not request.user.es_paciente():
        return redirect('cuentas:redireccion')

    usuario = request.user
    prefs   = _get_prefs(usuario)
    errores = {}

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'datos':
            # Verificar permiso
            if prefs and not prefs.editar_datos_habilitado:
                messages.error(request, 'Tu especialista ha desactivado la edición de datos personales.')
                return redirect('cuentas:editar_perfil_paciente')

            first_name = request.POST.get('first_name', '').strip()
            last_name  = request.POST.get('last_name', '').strip()
            email      = request.POST.get('email', '').strip().lower()

            if not email:
                errores['email'] = 'El correo es obligatorio.'
            elif Usuario.objects.filter(email=email).exclude(pk=usuario.pk).exists():
                errores['email'] = 'Ese correo ya está registrado por otro usuario.'

            if not errores:
                usuario.first_name = first_name
                usuario.last_name  = last_name
                usuario.email      = email
                usuario.save(update_fields=['first_name', 'last_name', 'email'])
                messages.success(request, 'Tus datos fueron actualizados correctamente.')
                return redirect('cuentas:editar_perfil_paciente')

        elif accion == 'contrasena':
            # Verificar permiso
            if prefs and not prefs.cambiar_contrasena_habilitado:
                messages.error(request, 'Tu especialista ha desactivado el cambio de contraseña.')
                return redirect('cuentas:editar_perfil_paciente')

            contrasena_actual = request.POST.get('contrasena_actual', '')
            nueva             = request.POST.get('nueva_contrasena', '')
            confirmacion      = request.POST.get('confirmar_contrasena', '')

            if not usuario.check_password(contrasena_actual):
                errores['contrasena_actual'] = 'La contraseña actual no es correcta.'
            elif len(nueva) < 8:
                errores['nueva_contrasena'] = 'La nueva contraseña debe tener al menos 8 caracteres.'
            elif nueva != confirmacion:
                errores['confirmar_contrasena'] = 'Las contraseñas no coinciden.'

            if not errores:
                usuario.set_password(nueva)
                usuario.save()
                update_session_auth_hash(request, usuario)
                messages.success(request, 'Tu contraseña fue actualizada correctamente.')
                return redirect('cuentas:editar_perfil_paciente')

    recordatorio = None
    try:
        recordatorio = usuario.recordatorio_email
    except Exception:
        pass

    return render(request, 'cuentas/editar_perfil.html', {
        'usuario':      usuario,
        'prefs':        prefs,
        'errores':      errores,
        'recordatorio': recordatorio,
    })
