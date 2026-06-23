# Reexporta todas las vistas de cuentas para mantener compatibilidad con urls.py
from .registro import registro_especialista  # HU-001, HU-002
from .login import redireccion_por_rol, perfil_paciente  # HU-004
from .dashboard_admin import dashboard_admin, aprobar_especialista, rechazar_especialista  # HU-006
from .gestionar_usuario import desactivar_usuario, reactivar_usuario, eliminar_usuario  # gestión de cuentas
from .estado_animo import registrar_animo  # HU-022
from .calendario_animo import calendario_animo  # HU-024
from .eliminar_cuenta import confirmar_eliminacion, cuenta_eliminada  # HU-010
from .pregunta_diaria_paciente import responder_pregunta_diaria, historial_pregunta_diaria  # HU-026
from .recordatorio import configurar_recordatorio  # HU-027
