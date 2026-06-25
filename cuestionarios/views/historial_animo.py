import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# ¡AHORA IMPORTAMOS DESDE CUENTAS, DONDE JOAQUÍN CREÓ EL MODELO!
from cuentas.models import RegistroAnimo 

@login_required
def historial_animo(request):
    # Traemos los registros de Joaquín
    registros_queryset = RegistroAnimo.objects.filter(paciente=request.user)
    
    # Para el gráfico, ordenamos cronológicamente (el más antiguo primero a la izquierda)
    registros_grafico = list(registros_queryset.order_by('fecha'))

    fechas = []
    niveles = []

    for registro in registros_grafico:
        fechas.append(registro.fecha.strftime('%d-%m-%Y'))
        niveles.append(registro.valor) # Usamos "valor" (1-10) de Joaquín

    contexto = {
        'fechas_json': json.dumps(fechas),
        'niveles_json': json.dumps(niveles),
        'registros_tabla': registros_queryset # La tabla muestra el más reciente primero
    }
    
    return render(request, 'cuestionarios/historial_animo.html', contexto)
