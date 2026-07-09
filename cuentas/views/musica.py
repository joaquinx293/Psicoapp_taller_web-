# HU-029 + HU-033: Gestión de pistas musicales (admin) + endpoint JSON para el reproductor
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from cuentas.models import PistaMusical, LogCambioMusica

FORMATOS_VALIDOS = {'.mp3', '.ogg', '.wav', '.flac', '.aac', '.m4a'}
TAMANIO_MAX_MB   = 100
TAMANIO_MAX_BYTES = TAMANIO_MAX_MB * 1024 * 1024


def _log(admin, accion, pista_titulo, detalle=''):
    """Registra un cambio en el log de auditoría."""
    LogCambioMusica.objects.create(
        admin=admin,
        accion=accion,
        pista_titulo=pista_titulo,
        detalle=detalle,
    )


# ─── Endpoint JSON para el reproductor del paciente ───────────────────────────

@login_required
def pistas_json(request):
    """Devuelve lista JSON de pistas activas para el reproductor."""
    pistas = PistaMusical.objects.filter(activa=True).order_by('orden', 'id')
    data = [
        {
            'id':     p.pk,
            'titulo': p.titulo,
            'url':    request.build_absolute_uri(p.archivo.url),
        }
        for p in pistas
    ]
    return JsonResponse({'pistas': data})


# ─── Panel admin ──────────────────────────────────────────────────────────────

@login_required
def gestionar_musica(request):
    if not (request.user.es_admin() or request.user.is_superuser):
        return redirect('cuentas:redireccion')

    if request.method == 'POST':
        titulo  = request.POST.get('titulo', '').strip()
        archivo = request.FILES.get('archivo')

        if not titulo:
            messages.error(request, 'El título es obligatorio.')
        elif not archivo:
            messages.error(request, 'Debes seleccionar un archivo de audio.')
        else:
            extension = os.path.splitext(archivo.name)[1].lower()
            if extension not in FORMATOS_VALIDOS:
                messages.error(
                    request,
                    f'Formato no permitido ({extension or "sin extensión"}). '
                    'Usa MP3, OGG, WAV, FLAC, AAC o M4A.'
                )
            elif archivo.size > TAMANIO_MAX_BYTES:
                mb = archivo.size / (1024 * 1024)
                messages.error(
                    request,
                    f'El archivo pesa {mb:.1f} MB. El máximo permitido es {TAMANIO_MAX_MB} MB.'
                )
            else:
                orden_max = PistaMusical.objects.count()
                pista = PistaMusical.objects.create(
                    titulo=titulo,
                    archivo=archivo,
                    orden=orden_max,
                    activa=True,
                )
                _log(
                    request.user,
                    LogCambioMusica.ACCION_SUBIR,
                    titulo,
                    detalle=f'{extension.lstrip(".")} · {archivo.size // 1024} KB'
                )
                messages.success(request, f'Pista "{titulo}" agregada correctamente.')

        return redirect('cuentas:gestionar_musica')

    pistas = PistaMusical.objects.all()
    logs   = LogCambioMusica.objects.select_related('admin')[:50]
    return render(request, 'cuentas/gestionar_musica.html', {
        'pistas': pistas,
        'logs':   logs,
    })


@login_required
@require_POST
def eliminar_pista(request, pk):
    if not (request.user.es_admin() or request.user.is_superuser):
        return redirect('cuentas:redireccion')

    pista = get_object_or_404(PistaMusical, pk=pk)
    titulo = pista.titulo

    # Eliminar el archivo físico
    try:
        if pista.archivo and os.path.isfile(pista.archivo.path):
            os.remove(pista.archivo.path)
    except Exception:
        pass

    pista.delete()
    _log(request.user, LogCambioMusica.ACCION_ELIMINAR, titulo)
    messages.success(request, f'Pista "{titulo}" eliminada.')
    return redirect('cuentas:gestionar_musica')


@login_required
@require_POST
def toggle_pista(request, pk):
    if not (request.user.es_admin() or request.user.is_superuser):
        return redirect('cuentas:redireccion')

    pista = get_object_or_404(PistaMusical, pk=pk)
    pista.activa = not pista.activa
    pista.save(update_fields=['activa'])

    accion = LogCambioMusica.ACCION_ACTIVAR if pista.activa else LogCambioMusica.ACCION_DESACTIVAR
    _log(request.user, accion, pista.titulo)

    estado = 'activada' if pista.activa else 'desactivada'
    messages.success(request, f'Pista "{pista.titulo}" {estado}.')
    return redirect('cuentas:gestionar_musica')


@login_required
@require_POST
def subir_orden_pista(request, pk):
    if not (request.user.es_admin() or request.user.is_superuser):
        return redirect('cuentas:redireccion')

    pista = get_object_or_404(PistaMusical, pk=pk)
    anterior = PistaMusical.objects.filter(orden__lt=pista.orden).order_by('-orden').first()
    if anterior:
        pista.orden, anterior.orden = anterior.orden, pista.orden
        pista.save(update_fields=['orden'])
        anterior.save(update_fields=['orden'])
        _log(
            request.user,
            LogCambioMusica.ACCION_REORDENAR,
            pista.titulo,
            detalle=f'Intercambiada con "{anterior.titulo}"',
        )
    return redirect('cuentas:gestionar_musica')


@login_required
@require_POST
def bajar_orden_pista(request, pk):
    if not (request.user.es_admin() or request.user.is_superuser):
        return redirect('cuentas:redireccion')

    pista = get_object_or_404(PistaMusical, pk=pk)
    siguiente = PistaMusical.objects.filter(orden__gt=pista.orden).order_by('orden').first()
    if siguiente:
        pista.orden, siguiente.orden = siguiente.orden, pista.orden
        pista.save(update_fields=['orden'])
        siguiente.save(update_fields=['orden'])
        _log(
            request.user,
            LogCambioMusica.ACCION_REORDENAR,
            pista.titulo,
            detalle=f'Intercambiada con "{siguiente.titulo}"',
        )
    return redirect('cuentas:gestionar_musica')
