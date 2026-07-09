# HU-030: Favoritos del dato del día (paciente)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from cuentas.models import DatoDelDia, DatoFavorito, LogBienestar


@login_required
@require_POST
def toggle_favorito_dato(request, pk):
    """Agrega o quita un dato de los favoritos del paciente."""
    if not request.user.es_paciente():
        return redirect('cuentas:redireccion')

    dato = get_object_or_404(DatoDelDia, pk=pk, activo=True)

    favorito, creado = DatoFavorito.objects.get_or_create(
        paciente=request.user,
        dato=dato,
    )
    if creado:
        messages.success(request, '¡Dato guardado en tus favoritos!')
    else:
        favorito.delete()
        messages.info(request, 'Dato eliminado de tus favoritos.')
    # HU-038: registrar interacción con herramienta dato del día
    LogBienestar.objects.create(
        usuario=request.user,
        herramienta=LogBienestar.DATO_DIA,
    )

    # Redirigir de vuelta a donde vino (perfil o favoritos)
    next_url = request.POST.get('next', 'cuentas:perfil_paciente')
    return redirect(next_url)


@login_required
def mis_favoritos_datos(request):
    """Lista todos los datos marcados como favoritos por el paciente."""
    if not request.user.es_paciente():
        return redirect('cuentas:redireccion')

    # HU-038: registrar acceso a herramienta dato del día
    LogBienestar.objects.create(
        usuario=request.user,
        herramienta=LogBienestar.DATO_DIA,
    )

    favoritos = DatoFavorito.objects.filter(
        paciente=request.user
    ).select_related('dato').order_by('-fecha_guardado')

    return render(request, 'cuentas/mis_favoritos_datos.html', {
        'favoritos': favoritos,
    })
