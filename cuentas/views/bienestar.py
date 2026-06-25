# HU-028: Herramientas de Bienestar - Respiración Guiada
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from mantenedores.models import DatoDelDia


@login_required
def respiracion_guiada(request):
    """Muestra la interfaz del ejercicio de respiración para el paciente."""
    if not request.user.es_paciente():
        return redirect('cuentas:redireccion')

    return render(request, 'cuentas/respiracion.html')
    
@login_required
def toggle_favorito(request, dato_id):
    """Permite al paciente guardar o quitar un dato de sus favoritos."""
    if not request.user.es_paciente():
        return redirect('cuentas:redireccion')

    if request.method == 'POST':
        dato = get_object_or_404(DatoDelDia, id=dato_id)
        if request.user in dato.favoritos.all():
            dato.favoritos.remove(request.user)
        else:
            dato.favoritos.add(request.user)

    return redirect('cuentas:perfil_paciente')
