# HU-032: Gestión del dato del día (administrador)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from cuentas.models import DatoDelDia

MINIMO_ACTIVOS = 10
MAX_PALABRAS   = 100


def _validar_dato(texto, fuente, instancia_actual=None):
    """Valida texto y fuente; retorna dict de errores."""
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
        else:
            # Verificar duplicado (excluir la instancia actual si se está editando)
            qs = DatoDelDia.objects.filter(texto__iexact=texto)
            if instancia_actual:
                qs = qs.exclude(pk=instancia_actual.pk)
            if qs.exists():
                errores['texto'] = 'Ya existe un dato con ese mismo texto.'

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


# ─── Vista admin: carga masiva desde archivo TXT ──────────────────────────────

@login_required
@require_POST
def cargar_datos_desde_txt(request):
    if not (request.user.es_admin() or request.user.is_superuser):
        return redirect('cuentas:redireccion')

    archivo = request.FILES.get('archivo_txt')

    if not archivo:
        messages.error(request, 'Debes seleccionar un archivo .txt.')
        return redirect('cuentas:gestionar_datos_dia')

    if not archivo.name.lower().endswith('.txt'):
        messages.error(request, 'Solo se aceptan archivos con extensión .txt.')
        return redirect('cuentas:gestionar_datos_dia')

    fuente_global = request.POST.get('fuente_txt', '').strip()
    if not fuente_global:
        messages.error(request, 'La fuente es obligatoria para la carga masiva.')
        return redirect('cuentas:gestionar_datos_dia')

    try:
        contenido = archivo.read().decode('utf-8', errors='replace')
    except Exception:
        messages.error(request, 'No se pudo leer el archivo. Asegúrate de que sea texto UTF-8.')
        return redirect('cuentas:gestionar_datos_dia')

    fragmentos = [f.strip() for f in contenido.split('>') if f.strip()]

    if not fragmentos:
        messages.warning(request, 'El archivo no contiene datos separados por ">".')
        return redirect('cuentas:gestionar_datos_dia')

    creados   = 0
    omitidos  = 0  # duplicados
    con_error = []  # textos con demasiadas palabras

    for texto in fragmentos:
        palabras = DatoDelDia.contar_palabras(texto)
        if palabras > MAX_PALABRAS:
            con_error.append(f'"{texto[:40]}…" ({palabras} palabras)')
            continue

        if DatoDelDia.objects.filter(texto__iexact=texto).exists():
            omitidos += 1
            continue

        DatoDelDia.objects.create(texto=texto, fuente=fuente_global, activo=True)
        creados += 1

    # Resumen
    partes = []
    if creados:
        partes.append(f'{creados} dato{"s" if creados != 1 else ""} creado{"s" if creados != 1 else ""}')
    if omitidos:
        partes.append(f'{omitidos} omitido{"s" if omitidos != 1 else ""} por duplicado')
    if con_error:
        partes.append(f'{len(con_error)} con exceso de palabras')

    if creados:
        messages.success(request, 'Carga completada: ' + ', '.join(partes) + '.')
    else:
        messages.warning(request, 'No se creó ningún dato: ' + ', '.join(partes) + '.')

    if con_error:
        messages.warning(
            request,
            'Datos con demasiadas palabras (no creados): ' + ' | '.join(con_error)
        )

    return redirect('cuentas:gestionar_datos_dia')
