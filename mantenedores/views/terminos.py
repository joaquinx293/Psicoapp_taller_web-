# HU-031: Gestionar términos y condiciones
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import TerminosCondiciones


def _solo_admin(request):
    return request.user.is_authenticated and (
        request.user.es_admin() or request.user.is_superuser
    )


@login_required
def gestionar_terminos(request):
    if not _solo_admin(request):
        return redirect("cuentas:login")

    if request.method == "POST":
        rol = request.POST.get("rol", "").strip()
        contenido = request.POST.get("contenido", "").strip()
        if rol not in (TerminosCondiciones.ROL_PACIENTE, TerminosCondiciones.ROL_ESPECIALISTA):
            messages.error(request, "Tipo de usuario inválido.")
        elif not contenido:
            messages.error(request, "El contenido no puede estar vacío.")
        else:
            TerminosCondiciones.objects.filter(rol=rol, vigente=True).update(vigente=False)
            ultima = TerminosCondiciones.objects.filter(rol=rol).order_by("-version").first()
            nueva_version = (ultima.version + 1) if ultima else 1
            TerminosCondiciones.objects.create(
                rol=rol, version=nueva_version, contenido=contenido,
                autor=request.user, vigente=True,
            )
            messages.success(request, f"Versión {nueva_version} publicada.")
            return redirect("mantenedores:terminos")

    vigente_paciente     = TerminosCondiciones.get_vigente(rol=TerminosCondiciones.ROL_PACIENTE)
    vigente_especialista = TerminosCondiciones.get_vigente(rol=TerminosCondiciones.ROL_ESPECIALISTA)
    historial            = TerminosCondiciones.objects.all()
    return render(request, "mantenedores/terminos.html", {
        "vigente_paciente":     vigente_paciente,
        "vigente_especialista": vigente_especialista,
        "rol_choices":          TerminosCondiciones.ROL_CHOICES,
        "historial":            historial,
    })
