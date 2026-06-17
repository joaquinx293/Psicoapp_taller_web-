from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import TerminosCondiciones


@login_required
def gestionar_terminos(request):
    if not request.user.es_admin() and not request.user.is_superuser:
        return redirect('cuentas:login')

    if request.method == 'POST':
        contenido = request.POST.get('contenido', '').strip()
        if not contenido:
            messages.error(request, 'El contenido no puede estar vacío.')
        else:
            ultima = TerminosCondiciones.objects.order_by('-version').first()
            nueva_version = (ultima.version + 1) if ultima else 1
            TerminosCondiciones.objects.update(vigente=False)
            TerminosCondiciones.objects.create(
                version=nueva_version,
                contenido=contenido,
                autor=request.user,
                vigente=True,
            )
            messages.success(request, f'Versión {nueva_version} publicada correctamente.')
            return redirect('mantenedores:terminos')

    vigente = TerminosCondiciones.get_vigente()
    historial = TerminosCondiciones.objects.all().order_by('-version')
    return render(request, 'mantenedores/terminos.html', {
        'vigente': vigente,
        'historial': historial,
    })
