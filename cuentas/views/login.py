# HU-004: Iniciar sesión
# El LoginView de Django está configurado en urls.py.
# Este archivo contiene las vistas de soporte post-login.
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from ..models import RegistroAnimo, RespuestaPreguntaDiaria, RecordatorioEmail, DatoDelDia, DatoFavorito
from cuestionarios.models import AsignacionCuestionario, RespuestaCuestionario


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
    hoy = timezone.localdate()
    ahora = timezone.localtime().time()
    animo_hoy = None
    pregunta_diaria = None
    pregunta_ya_respondida = False

    if request.user.es_paciente():
        animo_hoy = RegistroAnimo.objects.filter(
            paciente=request.user, fecha=hoy
        ).first()

        # HU-026: mostrar card de pregunta diaria si está activa y es la hora
        try:
            config = request.user.pregunta_diaria
            if config.activa and ahora >= config.hora_inicio:
                pregunta_diaria = config
                pregunta_ya_respondida = RespuestaPreguntaDiaria.objects.filter(
                    pregunta_diaria=config, fecha=hoy
                ).exists()
        except Exception:
            pass

    # HU-027: recordatorio email
    recordatorio = None
    try:
        recordatorio = request.user.recordatorio_email
    except Exception:
        pass

    # HU-032 + HU-030: Dato del día y estado de favorito
    dato_del_dia = None
    dato_es_favorito = False
    cuestionarios_pendientes = 0
    if request.user.es_paciente():
        dato_del_dia = DatoDelDia.dato_de_hoy()
        if dato_del_dia:
            dato_es_favorito = DatoFavorito.objects.filter(
                paciente=request.user, dato=dato_del_dia
            ).exists()

        # Cuestionarios asignados que aún no han sido respondidos
        asignados_ids = AsignacionCuestionario.objects.filter(
            paciente=request.user, activa=True
        ).values_list('cuestionario_id', flat=True)
        respondidos_ids = RespuestaCuestionario.objects.filter(
            paciente=request.user, cuestionario_id__in=asignados_ids
        ).values_list('cuestionario_id', flat=True).distinct()
        cuestionarios_pendientes = len(set(asignados_ids) - set(respondidos_ids))

    return render(request, 'cuentas/perfil_paciente.html', {
        'animo_hoy': animo_hoy,
        'pregunta_diaria': pregunta_diaria,
        'pregunta_ya_respondida': pregunta_ya_respondida,
        'recordatorio': recordatorio,
        'dato_del_dia': dato_del_dia,
        'dato_es_favorito': dato_es_favorito,
        'cuestionarios_pendientes': cuestionarios_pendientes,
    })
