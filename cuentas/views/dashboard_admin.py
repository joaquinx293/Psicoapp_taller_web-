# HU-006: Dashboard del administrador
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from ..models import Usuario
from cuestionarios.models import Cuestionario


@login_required
def dashboard_admin(request):
    if not request.user.es_admin() and not request.user.is_superuser:
        return redirect("cuentas:login")
    total_pacientes     = Usuario.objects.filter(rol="paciente").count()
    total_especialistas = Usuario.objects.filter(rol="especialista", estado="activo").count()
    pendientes          = Usuario.objects.filter(rol="especialista", estado="pendiente")
    total_cuestionarios = Cuestionario.objects.count()
    especialistas       = Usuario.objects.filter(rol="especialista").order_by("estado", "first_name")
    pacientes           = Usuario.objects.filter(rol="paciente").order_by("estado", "first_name")
    en_revision         = Cuestionario.objects.filter(estado=Cuestionario.EN_REVISION).select_related("especialista")
    return render(request, "cuentas/dashboard_admin.html", {
        "total_pacientes":     total_pacientes,
        "total_especialistas": total_especialistas,
        "total_pendientes":    pendientes.count(),
        "total_cuestionarios": total_cuestionarios,
        "pendientes":          pendientes,
        "especialistas":       especialistas,
        "pacientes":           pacientes,
        "en_revision":         en_revision,
    })


@login_required
def aprobar_especialista(request, pk):
    if not request.user.es_admin() and not request.user.is_superuser:
        return redirect("cuentas:login")
    especialista = get_object_or_404(Usuario, pk=pk, rol="especialista")
    especialista.estado = "activo"
    especialista.motivo_rechazo = None
    especialista.save()
    messages.success(request, f"{especialista.get_full_name()} fue aprobado correctamente.")
    return redirect("cuentas:dashboard_admin")


@login_required
def rechazar_especialista(request, pk):
    if not request.user.es_admin() and not request.user.is_superuser:
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
