from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from cuentas.models import RegistroAnimo

Usuario = get_user_model()

@login_required
def ver_promedio_animo(request, paciente_pk):
    """HU-034: Ver promedio de estado de ánimo de un paciente (Archivo dedicado)"""
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    paciente = get_object_or_404(Usuario, pk=paciente_pk, rol='paciente')

    # Calcular promedio de los últimos 30 días
    hace_30_dias = timezone.localdate() - timedelta(days=30)
    resultado = RegistroAnimo.objects.filter(
        paciente=paciente,
        fecha__gte=hace_30_dias
    ).aggregate(promedio=Avg('valor'))

    promedio = resultado['promedio']
    color_animo = 'secondary'

    if promedio is not None:
        promedio = round(promedio, 1)
        if promedio >= 7:
            color_animo = 'success'
        elif promedio >= 4:
            color_animo = 'warning'
        else:
            color_animo = 'danger'

    return render(request, 'cuestionarios/promedio_animo.html', {
        'paciente': paciente,
        'promedio': promedio,
        'color_animo': color_animo,
    })
