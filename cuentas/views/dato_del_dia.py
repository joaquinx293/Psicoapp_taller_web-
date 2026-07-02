# HU-032: Gestión del dato del día (administrador)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from cuentas.models import DatoDelDia

MINIMO_ACTIVOS = 60
MAX_PALABRAS   = 100


def _validar_dato(texto, fuente, instancia_actual=None):
    """Valida texto y fuente; retorna lista de errores."""
    errores = {}
    texto  = texto.strip()
    fuente = fuente.strip()

    if not texto:
        errores['texto'] = 'El texto no puede estar vacío.'
    else:
        palabras = DatoDelDia.contar_palabras(texto)
        if palabras > MAX_PALABRAS:
            errores['texto'] = (
                f'El texto tiene {palabras} palabras. El máximo permitido es {MAX_PALABRAS}.'
            )

    if not fuente:
        errores['fuente'] = 'La fuente es obligatoria.'

    return errores


# ─── Vista admin: listar + crear ──────────────────────────────────────────────

@login_required
def gestionar_datos_dia(request):
    if not (request.user.es_admin() or request.user.is_superuser):
        return redirect('cuentas:redireccion')

    errores = {}
    form_data = {}

    if request.method == 'POST':
        texto  = request.POST.get('texto', '')
        fuente = request.POST.get('fuente', '')
        form_data = {'texto': texto, 'fuente': fuente}

        errores = _validar_dato(texto, fuente)

        if not errores:
            DatoDelDia.objects.create(
                texto=texto.strip(),
                fuente=fuente.strip(),
                activo=True,
            )
            messages.success(request, 'Dato del día creado correctamente.')
            return redirect('cuentas:gestionar_datos_dia')

    datos         = DatoDelDia.objects.all()
    total_activos = datos.filter(activo=True).count()
    faltan        = max(0, MINIMO_ACTIVOS - total_activos)

    return render(request, 'cuentas/gestionar_datos_dia.html', {
        'datos':         datos,
        'total_activos': total_activos,
        'minimo':        MINIMO_ACTIVOS,
        'faltan':        faltan,
        'errores':       errores,
        'form_data':     form_data,
        'max_palabras':  MAX_PALABRAS,
    })


# ─── Vista admin: editar ──────────────────────────────────────────────────────

@login_required
def editar_dato_dia(request, pk):
    if not (request.user.es_admin() or request.user.is_superuser):
        return redirect('cuentas:redireccion')

    dato    = get_object_or_404(DatoDelDia, pk=pk)
    errores = {}

    if request.method == 'POST':
        texto  = request.POST.get('texto', '')
        fuente = request.POST.get('fuente', '')

        errores = _validar_dato(texto, fuente, instancia_actual=dato)

        if not errores:
            dato.texto  = texto.strip()
            dato.fuente = fuente.strip()
            dato.save(update_fields=['texto', 'fuente', 'fecha_modificacion'])
            messages.success(request, 'Dato del día actualizado.')
            return redirect('cuentas:gestionar_datos_dia')

    return render(request, 'cuentas/editar_dato_dia.html', {
        'dato':         dato,
        'errores':      errores,
        'max_palabras': MAX_PALABRAS,
    })


# ─── Vista admin: activar / desactivar ────────────────────────────────────────

@login_required
@require_POST
def toggle_dato_dia(request, pk):
    if not (request.user.es_admin() or request.user.is_superuser):
        return redirect('cuentas:redireccion')

    dato = get_object_or_404(DatoDelDia, pk=pk)

    if dato.activo:
        # Verificar que queden al menos MINIMO_ACTIVOS tras desactivar
        activos_restantes = DatoDelDia.objects.filter(activo=True).count() - 1
        if activos_restantes < MINIMO_ACTIVOS:
            messages.error(
                request,
                f'No se puede desactivar: quedarían {activos_restantes} datos activos '
                f'(mínimo requerido: {MINIMO_ACTIVOS}).'
            )
            return redirect('cuentas:gestionar_datos_dia')
        dato.activo = False
        msg = f'Dato desactivado.'
    else:
        dato.activo = True
        msg = f'Dato activado.'

    dato.save(update_fields=['activo', 'fecha_modificacion'])
    messages.success(request, msg)
    return redirect('cuentas:gestionar_datos_dia')
