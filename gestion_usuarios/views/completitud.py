# HU-035: Tasa de completitud de cuestionarios de un paciente
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from cuestionarios.models import AsignacionCuestionario, Pregunta, RespuestaCuestionario
from ..models import InvitacionPaciente


@login_required
def completitud_paciente(request, paciente_id):
    """
    HU-035: El especialista ve la tasa de completitud de cuestionarios de un paciente.
    Incluye stats por cuestionario con filtro de periodo y listado de
    preguntas de cuestionarios que el paciente nunca ha completado.
    """
    if not request.user.es_especialista():
        return redirect('cuentas:login')

    # Verificar que este paciente pertenece al especialista
    invitacion = get_object_or_404(
        InvitacionPaciente,
        paciente_id=paciente_id,
        especialista=request.user,
    )
    if invitacion.paciente is None:
        return redirect('gestion_usuarios:listado_pacientes')

    paciente = invitacion.paciente

    # ── Parámetros del filtro ────────────────────────────────────────────────
    hoy = date.today()
    fecha_desde_str = request.GET.get('desde', '')
    fecha_hasta_str = request.GET.get('hasta', '')

    try:
        dt_desde = date.fromisoformat(fecha_desde_str) if fecha_desde_str else hoy - timedelta(days=90)
    except ValueError:
        dt_desde = hoy - timedelta(days=90)
    try:
        dt_hasta = date.fromisoformat(fecha_hasta_str) if fecha_hasta_str else hoy
    except ValueError:
        dt_hasta = hoy

    # ── Asignaciones del especialista a este paciente ────────────────────────
    asignaciones = (
        AsignacionCuestionario.objects
        .filter(paciente=paciente, especialista=request.user)
        .select_related('cuestionario')
        .order_by('-fecha_asignacion')
    )

    # ── Pre-calcular completaciones (todo el tiempo y en el periodo) ─────────
    # Queryset de TODAS las completaciones del paciente en los cuestionarios asignados
    cuest_ids = [a.cuestionario_id for a in asignaciones]

    completadas_total = {
        r['cuestionario_id']: r['total']
        for r in RespuestaCuestionario.objects
        .filter(paciente=paciente, cuestionario_id__in=cuest_ids)
        .values('cuestionario_id')
        .annotate(total=Count('id'))
    }

    completadas_periodo = {
        r['cuestionario_id']: r['total']
        for r in RespuestaCuestionario.objects
        .filter(
            paciente=paciente,
            cuestionario_id__in=cuest_ids,
            fecha_respuesta__date__gte=dt_desde,
            fecha_respuesta__date__lte=dt_hasta,
        )
        .values('cuestionario_id')
        .annotate(total=Count('id'))
    }

    # ── Construir filas ──────────────────────────────────────────────────────
    filas = []
    nunca_completados_ids = []  # cuestionarios con 0 completaciones (todo el tiempo)

    for asig in asignaciones:
        cid = asig.cuestionario_id
        total_all  = completadas_total.get(cid, 0)
        total_peri = completadas_periodo.get(cid, 0)
        max_int    = asig.intentos_maximos   # 0 = ilimitado

        # Tasa del periodo: completadas_periodo / max_intentos (si hay límite)
        if max_int > 0:
            tasa = round(total_peri / max_int * 100)
            tasa_display = f'{tasa}%'
        else:
            # Sin límite: mostramos la relación completadas / "sin límite"
            tasa = None
            tasa_display = '— (sin límite)'

        if total_all == 0:
            nunca_completados_ids.append(cid)

        filas.append({
            'cuestionario':    asig.cuestionario,
            'max_intentos':    max_int,
            'completados_all': total_all,
            'completados_periodo': total_peri,
            'tasa':            tasa,           # int o None
            'tasa_display':    tasa_display,
            'fecha_asignacion': asig.fecha_asignacion,
            'activa':          asig.activa,
        })

    # ── Preguntas de cuestionarios nunca completados ─────────────────────────
    preguntas_abandonadas = []
    if nunca_completados_ids:
        preg_qs = (
            Pregunta.objects
            .filter(cuestionario_id__in=nunca_completados_ids, activa=True)
            .select_related('cuestionario')
            .order_by('cuestionario__nombre', 'orden', 'id')
        )
        # Agrupar por cuestionario
        grupos = {}
        for p in preg_qs:
            cid = p.cuestionario_id
            if cid not in grupos:
                grupos[cid] = {'cuestionario': p.cuestionario, 'preguntas': []}
            grupos[cid]['preguntas'].append(p)
        preguntas_abandonadas = list(grupos.values())

    # ── Stats globales ───────────────────────────────────────────────────────
    total_asignados  = len(filas)
    total_con_respuestas = sum(1 for f in filas if f['completados_all'] > 0)
    total_completados_periodo = sum(f['completados_periodo'] for f in filas)
    tasa_global = (
        round(total_con_respuestas / total_asignados * 100)
        if total_asignados > 0 else 0
    )

    context = {
        'paciente':                  paciente,
        'invitacion':                invitacion,
        'filas':                     filas,
        'preguntas_abandonadas':     preguntas_abandonadas,
        'fecha_desde':               dt_desde.isoformat(),
        'fecha_hasta':               dt_hasta.isoformat(),
        'total_asignados':           total_asignados,
        'total_con_respuestas':      total_con_respuestas,
        'total_completados_periodo': total_completados_periodo,
        'tasa_global':               tasa_global,
    }
    return render(request, 'gestion_usuarios/completitud_paciente.html', context)
