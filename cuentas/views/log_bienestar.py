# HU-038: Frecuencia de uso de herramientas de bienestar
import csv
import json
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..models import LogBienestar


# ── Endpoint AJAX ─────────────────────────────────────────────────────────────

@login_required
@require_POST
def log_bienestar_uso(request):
    """
    Recibe accesos JS desde el reproductor de música y el ejercicio de respiración.
    Body JSON: {herramienta: str, duracion_segundos?: int}
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)

    herramienta = data.get('herramienta', '')
    duracion    = data.get('duracion_segundos')

    herramientas_validas = {h for h, _ in LogBienestar.HERRAMIENTAS}
    if herramienta not in herramientas_validas:
        return JsonResponse({'ok': False, 'error': 'herramienta inválida'}, status=400)

    dur = int(duracion) if isinstance(duracion, (int, float)) and duracion > 0 else None

    LogBienestar.objects.create(
        usuario=request.user,
        herramienta=herramienta,
        duracion_segundos=dur,
    )
    return JsonResponse({'ok': True})


# ── Vista admin ────────────────────────────────────────────────────────────────

HERRAMIENTA_INFO = {
    LogBienestar.RESPIRACION: {
        'label': 'Respiración guiada',
        'icon':  'bi-lungs',
        'color': '#0d6efd',
    },
    LogBienestar.MUSICA: {
        'label': 'Música ambiental',
        'icon':  'bi-music-note-beamed',
        'color': '#6f42c1',
    },
    LogBienestar.DATO_DIA: {
        'label': 'Dato del día / Favoritos',
        'icon':  'bi-lightbulb',
        'color': '#fd7e14',
    },
}


@login_required
def log_bienestar(request):
    """
    HU-038: Vista admin — frecuencia de uso de herramientas de bienestar.
    Muestra gráfico de barras comparativo, tabla con accesos y duración promedio (respiración),
    y permite exportar CSV.
    """
    if not (request.user.es_admin() or request.user.is_superuser):
        return redirect('cuentas:redireccion')

    # ── Filtro de periodo ────────────────────────────────────────────────────
    hoy = date.today()
    try:
        dt_desde = date.fromisoformat(request.GET.get('desde', '')) if request.GET.get('desde') else hoy - timedelta(days=30)
    except ValueError:
        dt_desde = hoy - timedelta(days=30)
    try:
        dt_hasta = date.fromisoformat(request.GET.get('hasta', '')) if request.GET.get('hasta') else hoy
    except ValueError:
        dt_hasta = hoy

    exportar_csv = request.GET.get('exportar') == '1'

    # ── Stats por herramienta en el periodo ──────────────────────────────────
    qs_base = LogBienestar.objects.filter(
        fecha__date__gte=dt_desde,
        fecha__date__lte=dt_hasta,
    )

    stats_qs = (
        qs_base
        .values('herramienta')
        .annotate(
            total=Count('id'),
            sesiones_con_dur=Count('id', filter=Q(duracion_segundos__isnull=False)),
            avg_dur=Avg('duracion_segundos'),
        )
    )
    stats_dict = {s['herramienta']: s for s in stats_qs}

    # Construir filas ordenadas
    filas = []
    for herramienta_key, info in HERRAMIENTA_INFO.items():
        s = stats_dict.get(herramienta_key, {})
        total         = s.get('total', 0)
        ses_con_dur   = s.get('sesiones_con_dur', 0)
        avg_dur       = s.get('avg_dur')
        filas.append({
            'key':          herramienta_key,
            'label':        info['label'],
            'icon':         info['icon'],
            'color':        info['color'],
            'total':        total,
            'sesiones_completadas': ses_con_dur,
            'avg_dur_seg':  round(avg_dur) if avg_dur else None,
            'avg_dur_min':  f"{int(avg_dur // 60)}m {int(avg_dur % 60)}s" if avg_dur else None,
        })

    # ── Export CSV ───────────────────────────────────────────────────────────
    if exportar_csv:
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = (
            f'attachment; filename="bienestar_{dt_desde}_{dt_hasta}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow([
            'Herramienta', 'Accesos en periodo',
            'Sesiones completas (resp.)', 'Duración promedio sesión (s)',
        ])
        for f in filas:
            writer.writerow([
                f['label'],
                f['total'],
                f['sesiones_completadas'] if f['key'] == LogBienestar.RESPIRACION else '—',
                f['avg_dur_seg']          if f['key'] == LogBienestar.RESPIRACION else '—',
            ])
        return response

    # ── Datos para Chart.js ──────────────────────────────────────────────────
    chart_labels = json.dumps([f['label'] for f in filas])
    chart_values = json.dumps([f['total'] for f in filas])
    chart_colors = json.dumps([info['color'] for info in HERRAMIENTA_INFO.values()])

    # ── Tendencia diaria (últimos N días, para líneas en el chart) ───────────
    # Simplificado: top level totals + periodo seleccionado
    total_global = qs_base.count()
    total_usuarios = qs_base.values('usuario').distinct().count()

    context = {
        'filas':           filas,
        'fecha_desde':     dt_desde.isoformat(),
        'fecha_hasta':     dt_hasta.isoformat(),
        'total_global':    total_global,
        'total_usuarios':  total_usuarios,
        'chart_labels':    chart_labels,
        'chart_values':    chart_values,
        'chart_colors':    chart_colors,
    }
    return render(request, 'cuentas/log_bienestar.html', context)
