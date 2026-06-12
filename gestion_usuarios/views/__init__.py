# Reexporta todas las vistas de gestion_usuarios para compatibilidad con urls.py
from .activar_paciente import ingresar_pin, completar_registro  # HU-003
from .invitar_paciente import invitar_paciente                  # HU-007
from .listado_pacientes import dashboard, listado_pacientes     # HU-008
