import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from cuentas.models import RegistroAnimo, PreferenciasVisibilidad


def _get_prefs(paciente):
    prefs, _ = PreferenciasVisibilidad.objects.get_or_create(paciente=paciente)
    return prefs


@login_required
def historial_animo(request):
    if not request.user.es_paciente():
        return redirect('cuentas:redireccion')

    # Verificar permiso de visibilidad
    prefs = _get_prefs(request.user)
    if not prefs.ver_historial_animo_habilitado:
        return render(request, 'cuestionarios/seccion_no_disponible.html', {
            'seccion': 'el historial de ánimo',
        })

    registros_queryset = RegistroAnimo.objects.filter(paciente=request.user)
    registros_grafico  = list(registros_queryset.order_by('fecha'))

    fechas  = [r.fecha.strftime('%d-%m-%Y') for r in registros_grafico]
    niveles = [r.valor for r in registros_grafico]

    return render(request, 'cuestionarios/historial_animo.html', {
        'fechas_json':    json.dumps(fechas),
        'niveles_json':   json.dumps(niveles),
        'registros_tabla': registros_queryset,
    })
