# HU-004: Iniciar sesión
# El LoginView de Django está configurado en urls.py.
# Este archivo contiene las vistas de soporte post-login.
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required


@login_required
def redireccion_por_rol(request):
    if request.user.es_admin() or request.user.is_superuser:
        return redirect('cuentas:dashboard_admin')
    elif request.user.es_especialista():
        return redirect('gestion_usuarios:dashboard')
    else:
        return redirect('cuentas:perfil_paciente')


@login_required
def perfil_paciente(request):
    return render(request, 'cuentas/perfil_paciente.html')
