# HU-024: Visualizar calendario emocional 
import calendar
from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..models import RegistroAnimo, Usuario



def _construir_calendario(paciente, año, mes):
    """Devuelve una lista de semanas; cada semana es una lista de (dia, registro|None)."""
    cal = calendar.monthcalendar(año, mes)
    registros = {
        r.fecha.day: r
        for r in RegistroAnimo.objects.filter(
            paciente=paciente,
            fecha__year=año,
            fecha__month=mes,
        )
    }
    semanas = []
    for semana in cal:
        fila = []
        for dia in semana:
            if dia == 0:
                fila.append((None, None))
            else:
                fila.append((dia, registros.get(dia)))
        semanas.append(fila)
    return semanas




def _nav_mes(año, mes, delta):
    """Avanza o retrocede 'delta' meses y devuelve nuevo_año, nuevo_mes."""
    mes += delta
    if mes > 12:
        mes = 1
        año += 1
    elif mes < 1:
        mes = 12
        año -= 1
    return año, mes
@login_required
def calendario_animo(request, paciente_id=None):
    """
    Sin paciente_id el paciente ve su propio calendario.
    Con paciente_id el especialista ve el calendario de ese paciente en su perfil .
    """
    hoy = date.today()




    if paciente_id is not None:
        if not (request.user.es_especialista() or request.user.es_admin() or request.user.is_superuser):
            return redirect('cuentas:login')
        paciente = get_object_or_404(Usuario, pk=paciente_id, rol=Usuario.ROL_PACIENTE)
        vista_especialista = True
    else:
        if not request.user.es_paciente():
            return redirect('cuentas:redireccion')
        paciente = request.user
        vista_especialista = False
    try:
        año = int(request.GET.get('año', hoy.year))
        mes  = int(request.GET.get('mes',  hoy.month))
        # Limitar a rango razonable
        mes  = max(1, min(12, mes))
        año = max(2020, min(2100, año))
    except (ValueError, TypeError):
        año, mes = hoy.year, hoy.month

    semanas = _construir_calendario(paciente, año, mes)
    año_ant, mes_ant = _nav_mes(año, mes, -1)
    año_sig, mes_sig = _nav_mes(año, mes,  1)
    _MESES_ES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    nombre_mes = _MESES_ES[mes]
    dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    return render(request, 'cuentas/calendario_animo.html', {
        'paciente':         paciente,
        'vista_especialista': vista_especialista,
        'semanas':          semanas,
        'nombre_mes':       nombre_mes,
        'mes':              mes,
        'año':             año,
        'mes_ant':          mes_ant,
        'año_ant':         año_ant,
        'mes_sig':          mes_sig,
        'año_sig':         año_sig,
        'dias_semana':      dias_semana,
        'hoy':              hoy,
    })
