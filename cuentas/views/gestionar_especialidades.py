# Admin: gestión de categorías de especialidad
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from ..models import Especialidad, Usuario


def _solo_admin(request):
    return request.user.is_authenticated and (
        request.user.es_admin() or request.user.is_superuser
    )


@login_required
def gestionar_especialidades(request):
    """Listado + creación de especialidades."""
    if not _solo_admin(request):
        return redirect('cuentas:redireccion')

    if request.method == 'POST' and request.POST.get('accion') == 'crear':
        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            messages.error(request, 'El nombre no puede estar vacío.')
        elif Especialidad.objects.filter(nombre__iexact=nombre).exists():
            messages.error(request, f'Ya existe una especialidad con el nombre "{nombre}".')
        else:
            Especialidad.objects.create(nombre=nombre)
            messages.success(request, f'Especialidad "{nombre}" creada correctamente.')
        return redirect('cuentas:gestionar_especialidades')

    especialidades = Especialidad.objects.annotate(
        total_especialistas=Count(
            'especialistas',
            filter=Q(
                especialistas__rol=Usuario.ROL_ESPECIALISTA,
                especialistas__is_active=True,
            )
        )
    ).order_by('nombre')

    return render(request, 'cuentas/gestionar_especialidades.html', {
        'especialidades': especialidades,
    })


@login_required
def editar_especialidad(request, pk):
    """Editar el nombre de una especialidad."""
    if not _solo_admin(request):
        return redirect('cuentas:redireccion')

    especialidad = get_object_or_404(Especialidad, pk=pk)

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            messages.error(request, 'El nombre no puede estar vacío.')
        elif Especialidad.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
            messages.error(request, f'Ya existe otra especialidad con el nombre "{nombre}".')
        else:
            especialidad.nombre = nombre
            especialidad.save()
            messages.success(request, f'Especialidad actualizada a "{nombre}".')
            return redirect('cuentas:gestionar_especialidades')

    return render(request, 'cuentas/editar_especialidad.html', {
        'especialidad': especialidad,
    })


@login_required
def eliminar_especialidad(request, pk):
    """Eliminar especialidad solo si no tiene especialistas activos asignados."""
    if not _solo_admin(request):
        return redirect('cuentas:redireccion')
    if request.method != 'POST':
        return redirect('cuentas:gestionar_especialidades')

    especialidad = get_object_or_404(Especialidad, pk=pk)

    tiene_especialistas = Usuario.objects.filter(
        especialidad=especialidad,
        rol=Usuario.ROL_ESPECIALISTA,
    ).exists()

    if tiene_especialistas:
        messages.error(
            request,
            f'No se puede eliminar "{especialidad.nombre}": tiene especialistas asignados. '
            'Reasigna o desactiva los especialistas primero.'
        )
    else:
        nombre = especialidad.nombre
        especialidad.delete()
        messages.success(request, f'Especialidad "{nombre}" eliminada.')

    return redirect('cuentas:gestionar_especialidades')
