# HU-006: Dashboard del administrador
import uuid

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from ..models import Notificacion, Usuario
from cuestionarios.models import Cuestionario


def _solo_admin(request):
    return request.user.is_authenticated and (
        request.user.es_admin() or request.user.is_superuser
    )


@login_required
def dashboard_admin(request):
    if not _solo_admin(request):
        return redirect("cuentas:login")

    total_pacientes     = Usuario.objects.filter(rol="paciente").count()
    total_especialistas = Usuario.objects.filter(rol="especialista", estado="activo").count()
    pendientes          = Usuario.objects.filter(rol="especialista", estado="pendiente")
    total_cuestionarios = Cuestionario.objects.count()
    en_revision         = Cuestionario.objects.filter(estado=Cuestionario.BORRADOR).select_related("especialista")

    # ── Búsqueda, filtros y paginación de usuarios ──────────────────────────────
    q      = request.GET.get('q', '').strip()
    f_rol  = request.GET.get('rol', '')
    f_est  = request.GET.get('estado', '')

    usuarios_qs = Usuario.objects.exclude(is_superuser=True).order_by('rol', 'estado', 'first_name', 'username')

    if q:
        usuarios_qs = usuarios_qs.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)  |
            Q(username__icontains=q)   |
            Q(email__icontains=q)
        )
    if f_rol:
        usuarios_qs = usuarios_qs.filter(rol=f_rol)
    if f_est:
        usuarios_qs = usuarios_qs.filter(estado=f_est)

    paginator   = Paginator(usuarios_qs, 20)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)

    # Solicitudes de baja pendientes
    solicitudes_baja = Notificacion.objects.filter(
        tipo__in=[
            Notificacion.TIPO_BAJA_PACIENTE,
            Notificacion.TIPO_BAJA_ESPECIALISTA,
        ],
        leida=False,
    ).select_related('solicitante')

    return render(request, "cuentas/dashboard_admin.html", {
        "total_pacientes":     total_pacientes,
        "total_especialistas": total_especialistas,
        "total_pendientes":    pendientes.count(),
        "total_cuestionarios": total_cuestionarios,
        "pendientes":          pendientes,
        "en_revision":         en_revision,
        "solicitudes_baja":    solicitudes_baja,
        # Tabla unificada de usuarios
        "page_obj":  page_obj,
        "q":         q,
        "f_rol":     f_rol,
        "f_est":     f_est,
        "roles":     Usuario.ROLES,
        "estados":   Usuario.ESTADOS,
    })


@login_required
def aprobar_especialista(request, pk):
    if not _solo_admin(request):
        return redirect("cuentas:login")
    especialista = get_object_or_404(Usuario, pk=pk, rol="especialista")
    especialista.estado = "activo"
    especialista.motivo_rechazo = None
    especialista.save()
    messages.success(request, f"{especialista.get_full_name()} fue aprobado correctamente.")
    return redirect("cuentas:dashboard_admin")


@login_required
def rechazar_especialista(request, pk):
    if not _solo_admin(request):
        return redirect("cuentas:login")
    especialista = get_object_or_404(Usuario, pk=pk, rol="especialista")
    if request.method == "POST":
        motivo = request.POST.get("motivo", "").strip()
        if not motivo:
            messages.error(request, "Debes ingresar un motivo de rechazo.")
            return render(request, "cuentas/rechazar_especialista.html",
                          {"especialista": especialista})
        especialista.estado = "rechazado"
        especialista.motivo_rechazo = motivo
        especialista.save()
        messages.warning(request, f"{especialista.get_full_name()} fue rechazado.")
        return redirect("cuentas:dashboard_admin")
    return render(request, "cuentas/rechazar_especialista.html",
                  {"especialista": especialista})


# ── Baja de paciente ──────────────────────────────────────────────────────────

@login_required
def aprobar_baja_paciente(request, notificacion_pk):
    """Admin aprueba solicitud: anonimiza al paciente y marca notificación como leída."""
    if not _solo_admin(request):
        return redirect("cuentas:login")
    if request.method != "POST":
        return redirect("cuentas:dashboard_admin")

    notif = get_object_or_404(
        Notificacion,
        pk=notificacion_pk,
        tipo=Notificacion.TIPO_BAJA_PACIENTE,
        leida=False,
    )
    paciente = notif.solicitante

    if paciente:
        nombre_display = paciente.get_full_name() or paciente.username
        uid = uuid.uuid4().hex[:10]
        paciente.username      = f'anonimo_{uid}'
        paciente.first_name    = ''
        paciente.last_name     = ''
        paciente.email         = ''
        paciente.fecha_nacimiento = None
        paciente.motivo_rechazo   = None
        paciente.estado        = Usuario.INACTIVO
        paciente.is_active     = False
        paciente.set_unusable_password()
        paciente.save()
        messages.success(
            request,
            f'La cuenta de {nombre_display} fue anonimizada. '
            f'Sus datos clínicos se conservan sin identificación.'
        )
    else:
        messages.warning(request, 'El paciente ya no existe en el sistema.')

    notif.leida = True
    notif.save()
    return redirect("cuentas:dashboard_admin")


@login_required
def rechazar_baja_paciente(request, notificacion_pk):
    """Admin rechaza la solicitud de baja del paciente."""
    if not _solo_admin(request):
        return redirect("cuentas:login")
    if request.method != "POST":
        return redirect("cuentas:dashboard_admin")

    notif = get_object_or_404(
        Notificacion,
        pk=notificacion_pk,
        tipo=Notificacion.TIPO_BAJA_PACIENTE,
        leida=False,
    )

    # Notificar al paciente si aún existe
    paciente = notif.solicitante
    if paciente:
        Notificacion.objects.create(
            destinatario=paciente,
            tipo=Notificacion.TIPO_GENERAL,
            mensaje=(
                'Tu solicitud de eliminación de cuenta fue revisada por el administrador '
                'y no fue aprobada en este momento. Tu cuenta permanece activa.'
            ),
        )
        messages.info(
            request,
            f'Solicitud de {paciente.get_full_name() or paciente.username} rechazada. '
            f'Se le notificó que su cuenta permanece activa.'
        )
    else:
        messages.info(request, 'Solicitud rechazada (el paciente ya no existe).')

    notif.leida = True
    notif.save()
    return redirect("cuentas:dashboard_admin")


# ── Baja de especialista ──────────────────────────────────────────────────────

@login_required
def ver_impacto_baja_especialista(request, notificacion_pk):
    """Muestra al admin el impacto de aprobar la baja del especialista."""
    if not _solo_admin(request):
        return redirect("cuentas:login")

    notif = get_object_or_404(
        Notificacion,
        pk=notificacion_pk,
        tipo=Notificacion.TIPO_BAJA_ESPECIALISTA,
        leida=False,
    )
    especialista = notif.solicitante

    from cuestionarios.models import AsignacionCuestionario, Cuestionario as CModel
    impacto = {}
    if especialista:
        asignaciones_activas = AsignacionCuestionario.objects.filter(
            especialista=especialista, activa=True
        ).select_related('paciente', 'cuestionario')
        cuestionarios_propios = CModel.objects.filter(especialista=especialista)
        impacto = {
            'asignaciones_activas': asignaciones_activas,
            'total_asignaciones':   asignaciones_activas.count(),
            'cuestionarios_propios': cuestionarios_propios,
            'total_cuestionarios':  cuestionarios_propios.count(),
        }

    return render(request, 'cuentas/confirmar_baja_especialista.html', {
        'notif':        notif,
        'especialista': especialista,
        'impacto':      impacto,
    })


@login_required
def aprobar_baja_especialista(request, notificacion_pk):
    """Admin aprueba: desactiva al especialista lógicamente."""
    if not _solo_admin(request):
        return redirect("cuentas:login")
    if request.method != "POST":
        return redirect("cuentas:dashboard_admin")

    notif = get_object_or_404(
        Notificacion,
        pk=notificacion_pk,
        tipo=Notificacion.TIPO_BAJA_ESPECIALISTA,
        leida=False,
    )
    especialista = notif.solicitante

    if especialista:
        nombre_display = especialista.get_full_name() or especialista.username
        especialista.estado    = Usuario.INACTIVO
        especialista.is_active = False
        especialista.save()

        # Notificar al especialista
        Notificacion.objects.create(
            destinatario=especialista,
            tipo=Notificacion.TIPO_GENERAL,
            mensaje=(
                'Tu solicitud de baja fue aprobada. Tu cuenta ha sido desactivada. '
                'Tus registros clínicos se conservan en el sistema.'
            ),
        )
        messages.success(
            request,
            f'La cuenta del/la especialista {nombre_display} fue desactivada.'
        )
    else:
        messages.warning(request, 'El especialista ya no existe en el sistema.')

    notif.leida = True
    notif.save()
    return redirect("cuentas:dashboard_admin")


@login_required
def rechazar_baja_especialista(request, notificacion_pk):
    """Admin rechaza la solicitud de baja del especialista."""
    if not _solo_admin(request):
        return redirect("cuentas:login")
    if request.method != "POST":
        return redirect("cuentas:dashboard_admin")

    notif = get_object_or_404(
        Notificacion,
        pk=notificacion_pk,
        tipo=Notificacion.TIPO_BAJA_ESPECIALISTA,
        leida=False,
    )
    especialista = notif.solicitante

    if especialista:
        Notificacion.objects.create(
            destinatario=especialista,
            tipo=Notificacion.TIPO_GENERAL,
            mensaje=(
                'Tu solicitud de baja fue revisada por el administrador '
                'y no fue aprobada. Tu cuenta permanece activa.'
            ),
        )
        messages.info(
            request,
            f'Solicitud de {especialista.get_full_name() or especialista.username} rechazada.'
        )
    else:
        messages.info(request, 'Solicitud rechazada (el especialista ya no existe).')

    notif.leida = True
    notif.save()
    return redirect("cuentas:dashboard_admin")
