# HU-037: Vista de administrador — Inicios de sesión por usuario
import csv
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from ..models import LogInicioSesion, Usuario


# ── Constantes ────────────────────────────────────────────────────────────────
ACTIVO_UMBRAL_DIAS = 30   # usuarios con al menos 1 sesión en los últimos N días


def _make_row(usuario, total_sesiones, ultima_sesion, es_activo, anonimizar):
    """Devuelve un dict con los datos de una fila, anonimizando si corresponde."""
    if anonimizar and usuario.rol == Usuario.ROL_PACIENTE:
        nombre_display = f'Paciente #{usuario.pk}'
        email_display  = '—'
    else:
        nombre_display = usuario.get_full_name() or usuario.username
        email_display  = usuario.email

    return {
        'usuario':         usuario,
        'nombre_display':  nombre_display,
        'email_display':   email_display,
        'rol':             usuario.get_rol_display(),
        'total_sesiones':  total_sesiones,
        'ultima_sesion':   ultima_sesion,
        'es_activo':       es_activo,
        'anonimizado':     anonimizar and usuario.rol == Usuario.ROL_PACIENTE,
    }


@login_required
def log_sesiones(request):
    """
    HU-037: Tabla de inicios de sesión por usuario.
    Sólo accesible para administradores.
    """
    if not (request.user.es_admin() or request.user.is_superuser):
        return redirect('cuentas:redireccion')

    # ── Parámetros del filtro ────────────────────────────────────────────────
    hoy          = date.today()
    fecha_desde  = request.GET.get('desde', '')
    fecha_hasta  = request.GET.get('hasta', '')
    filtro_rol   = request.GET.get('rol', '')
    exportar_csv = request.GET.get('exportar') == '1'

    # Valores por defecto: últimos 30 días
    try:
        dt_desde = date.fromisoformat(fecha_desde) if fecha_desde else hoy - timedelta(days=30)
    except ValueError:
        dt_desde = hoy - timedelta(days=30)
    try:
        dt_hasta = date.fromisoformat(fecha_hasta) if fecha_hasta else hoy
    except ValueError:
        dt_hasta = hoy

    # ── Construir queryset base ──────────────────────────────────────────────
    logs_qs = LogInicioSesion.objects.filter(
        fecha__date__gte=dt_desde,
        fecha__date__lte=dt_hasta,
    )

    # ── Agregar por usuario ──────────────────────────────────────────────────
    conteos = (
        logs_qs
        .values('usuario_id')
        .annotate(
            total=Count('id'),
            ultima=Max('fecha'),
        )
    )
    conteos_dict = {r['usuario_id']: r for r in conteos}

    # ── Fecha límite para considerar "activo" ────────────────────────────────
    limite_activo = timezone.now() - timedelta(days=ACTIVO_UMBRAL_DIAS)
    activos_ids = set(
        LogInicioSesion.objects
        .filter(fecha__gte=limite_activo)
        .values_list('usuario_id', flat=True)
        .distinct()
    )

    # ── Usuarios a mostrar ───────────────────────────────────────────────────
    usuarios_qs = Usuario.objects.filter(is_active=True).order_by('rol', 'username')
    if filtro_rol in (Usuario.ROL_PACIENTE, Usuario.ROL_ESPECIALISTA, Usuario.ROL_ADMIN):
        usuarios_qs = usuarios_qs.filter(rol=filtro_rol)

    # Construir filas
    filas = []
    for u in usuarios_qs:
        datos = conteos_dict.get(u.pk, {'total': 0, 'ultima': None})
        filas.append(_make_row(
            usuario        = u,
            total_sesiones = datos['total'],
            ultima_sesion  = datos['ultima'],
            es_activo      = u.pk in activos_ids,
            anonimizar     = True,
        ))

    # Ordenar: más sesiones primero
    filas.sort(key=lambda r: r['total_sesiones'], reverse=True)

    # ── Export CSV ───────────────────────────────────────────────────────────
    if exportar_csv:
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = (
            f'attachment; filename="sesiones_{dt_desde}_{dt_hasta}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow([
            'Nombre / ID', 'Email', 'Rol',
            'Inicios de sesión (periodo)', 'Última sesión',
            'Estado (últimos 30 días)',
        ])
        for f in filas:
            writer.writerow([
                f['nombre_display'],
                f['email_display'],
                f['rol'],
                f['total_sesiones'],
                f['ultima_sesion'].strftime('%d/%m/%Y %H:%M') if f['ultima_sesion'] else '—',
                'Activo' if f['es_activo'] else 'Inactivo',
            ])
        return response

    # ── Estadísticas rápidas para el encabezado ──────────────────────────────
    total_eventos = logs_qs.count()
    total_usuarios_con_sesion = len(conteos_dict)
    total_activos  = len(activos_ids)
    total_usuarios = usuarios_qs.count()

    context = {
        'filas':                     filas,
        'fecha_desde':               dt_desde.isoformat(),
        'fecha_hasta':               dt_hasta.isoformat(),
        'filtro_rol':                filtro_rol,
        'total_eventos':             total_eventos,
        'total_usuarios_con_sesion': total_usuarios_con_sesion,
        'total_activos':             total_activos,
        'total_usuarios':            total_usuarios,
        'activo_umbral_dias':        ACTIVO_UMBRAL_DIAS,
        'roles': [
            ('', 'Todos los roles'),
            (Usuario.ROL_PACIENTE,     'Pacientes'),
            (Usuario.ROL_ESPECIALISTA, 'Especialistas'),
            (Usuario.ROL_ADMIN,        'Administradores'),
        ],
    }
    return render(request, 'cuentas/log_sesiones.html', context)
