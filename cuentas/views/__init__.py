# Reexporta todas las vistas de cuentas para mantener compatibilidad con urls.py
from .registro import registro_especialista  # HU-001, HU-002
from .login import redireccion_por_rol, perfil_paciente  # HU-004
from .dashboard_admin import dashboard_admin, aprobar_especialista, rechazar_especialista  # HU-006
from .gestionar_usuario import desactivar_usuario, reactivar_usuario, eliminar_usuario  # gestión de cuentas
