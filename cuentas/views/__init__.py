# Reexporta todas las vistas de cuentas para mantener compatibilidad con urls.py
from .registro import registro_especialista  # HU-001, HU-002
from .login import redireccion_por_rol, perfil_paciente  # HU-004
