# Reexporta todas las vistas de cuentas para mantener compatibilidad con urls.py
from .registro import registro_especialista  # HU-001, HU-002
from .login import redireccion_por_rol, perfil_paciente  # HU-004
from .dashboard_admin import (  # HU-006 + gestión de bajas
    dashboard_admin,
    aprobar_especialista,
    rechazar_especialista,
    aprobar_baja_paciente,
    rechazar_baja_paciente,
    ver_impacto_baja_especialista,
    aprobar_baja_especialista,
    rechazar_baja_especialista,
)
from .gestionar_usuario import desactivar_usuario, reactivar_usuario, eliminar_usuario  # gestión de cuentas
from .estado_animo import registrar_animo  # HU-022
from .calendario_animo import calendario_animo  # HU-024
from .eliminar_cuenta import confirmar_eliminacion, cuenta_eliminada, cuenta_en_revision  # HU-010
from .solicitar_baja import solicitar_baja_especialista  # baja especialista
from .pregunta_diaria_paciente import responder_pregunta_diaria, historial_pregunta_diaria  # HU-026
from .recordatorio import configurar_recordatorio  # HU-027
from .bienestar import respiracion_guiada  # HU-028
from .editar_perfil import editar_perfil_paciente  # Cambio 4
from .visibilidad_paciente import configurar_visibilidad_paciente  # control de acceso
from .editar_usuario_admin import editar_usuario_admin  # gestión usuarios admin
from .favoritos_dato import toggle_favorito_dato, mis_favoritos_datos  # HU-030
from .dato_del_dia import (                         # HU-032
    gestionar_datos_dia,
    editar_dato_dia,
    toggle_dato_dia,
    cargar_datos_desde_txt,
)
from .musica import (                               # HU-029
    pistas_json,
    gestionar_musica,
    eliminar_pista,
    toggle_pista,
    subir_orden_pista,
    bajar_orden_pista,
)
from .log_sesiones import log_sesiones             # HU-037
from .log_bienestar import log_bienestar, log_bienestar_uso  # HU-038
from .gestionar_especialidades import (            # admin: categorías de especialidad
    gestionar_especialidades,
    editar_especialidad,
    eliminar_especialidad,
)
