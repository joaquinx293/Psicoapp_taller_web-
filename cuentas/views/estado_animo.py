# HU-022: Registrar estado de ánimo diario
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from ..models import RegistroAnimo


@login_required
def registrar_animo(request):
    """Permite al paciente registrar o editar su estado de ánimo del día."""
    if not request.user.es_paciente():
        return redirect('cuentas:redireccion')

    hoy = timezone.localdate()
    registro_hoy = RegistroAnimo.objects.filter(
        paciente=request.user, fecha=hoy
    ).first()

    if request.method == 'POST':
        try:
            valor = int(request.POST.get('valor', 0))
        except (ValueError, TypeError):
            valor = 0

        if not (1 <= valor <= 10):
            messages.error(request, 'Selecciona un valor entre 1 y 10.')
        else:
            if registro_hoy:
                registro_hoy.valor = valor
                registro_hoy.save()
                messages.success(request, 'Estado de ánimo actualizado.')
            else:
                RegistroAnimo.objects.create(
                    paciente=request.user,
                    fecha=hoy,
                    valor=valor,
                )
                messages.success(request, '¡Estado de ánimo registrado!')
            return redirect('cuentas:perfil_paciente')

    return render(request, 'cuentas/estado_animo.html', {
        'registro_hoy': registro_hoy,
        'hoy': hoy,
        'rango': range(1, 11),
    })
