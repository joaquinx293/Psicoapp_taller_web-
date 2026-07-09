# HU-028: Ejercicio de respiración guiada
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from ..models import LogBienestar


@login_required
def respiracion_guiada(request):
    """Muestra la interfaz del ejercicio de respiración guiada para el paciente."""
    if not request.user.es_paciente():
        return redirect('cuentas:redireccion')
    # HU-038: registrar acceso a herramienta de bienestar
    LogBienestar.objects.create(
        usuario=request.user,
        herramienta=LogBienestar.RESPIRACION,
    )
    return render(request, 'cuentas/respiracion.html')
