from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'cuentas'

urlpatterns = [
    path('registro/', views.registro_especialista, name='registro'),
    path('login/', auth_views.LoginView.as_view(
        template_name='cuentas/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('redireccion/', views.redireccion_por_rol, name='redireccion'),
    path('perfil/', views.perfil_paciente, name='perfil_paciente'),

    # HU-006: dashboard admin
    path('admin-dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('admin-dashboard/aprobar/<int:pk>/', views.aprobar_especialista, name='aprobar_especialista'),
    path('admin-dashboard/rechazar/<int:pk>/', views.rechazar_especialista, name='rechazar_especialista'),

    # Gestion de cuentas (desactivar / reactivar / eliminar)
    path('admin-dashboard/desactivar/<int:pk>/', views.desactivar_usuario, name='desactivar_usuario'),
    path('admin-dashboard/reactivar/<int:pk>/', views.reactivar_usuario, name='reactivar_usuario'),
    path('admin-dashboard/eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),

    # Gestión de solicitudes de baja (admin)
    path('admin-dashboard/baja/paciente/<int:notificacion_pk>/aprobar/',
         views.aprobar_baja_paciente, name='aprobar_baja_paciente'),
    path('admin-dashboard/baja/paciente/<int:notificacion_pk>/rechazar/',
         views.rechazar_baja_paciente, name='rechazar_baja_paciente'),
    path('admin-dashboard/baja/especialista/<int:notificacion_pk>/',
         views.ver_impacto_baja_especialista, name='ver_impacto_baja_especialista'),
    path('admin-dashboard/baja/especialista/<int:notificacion_pk>/aprobar/',
         views.aprobar_baja_especialista, name='aprobar_baja_especialista'),
    path('admin-dashboard/baja/especialista/<int:notificacion_pk>/rechazar/',
         views.rechazar_baja_especialista, name='rechazar_baja_especialista'),

    # HU-010: Solicitud de eliminación de cuenta (paciente)
    path('eliminar-cuenta/', views.confirmar_eliminacion, name='confirmar_eliminacion'),
    path('cuenta-eliminada/', views.cuenta_eliminada, name='cuenta_eliminada'),
    path('cuenta-en-revision/', views.cuenta_en_revision, name='cuenta_en_revision'),

    # Solicitud de baja (especialista)
    path('solicitar-baja/', views.solicitar_baja_especialista, name='solicitar_baja_especialista'),

    # HU-030: Favoritos del dato del día (paciente)
    path('favoritos/datos/',            views.mis_favoritos_datos,    name='mis_favoritos_datos'),
    path('favoritos/datos/<int:pk>/toggle/', views.toggle_favorito_dato, name='toggle_favorito_dato'),

    # HU-032: Dato del día (admin)
    path('datos-del-dia/',               views.gestionar_datos_dia,    name='gestionar_datos_dia'),
    path('datos-del-dia/<int:pk>/editar/', views.editar_dato_dia,      name='editar_dato_dia'),
    path('datos-del-dia/<int:pk>/toggle/', views.toggle_dato_dia,      name='toggle_dato_dia'),
    path('datos-del-dia/cargar-txt/',    views.cargar_datos_desde_txt, name='cargar_datos_desde_txt'),

    # HU-029: Música ambiental
    path('musica/pistas.json/', views.pistas_json, name='pistas_json'),
    path('musica/',             views.gestionar_musica, name='gestionar_musica'),
    path('musica/<int:pk>/eliminar/', views.eliminar_pista,     name='eliminar_pista'),
    path('musica/<int:pk>/toggle/',   views.toggle_pista,       name='toggle_pista'),
    path('musica/<int:pk>/subir/',    views.subir_orden_pista,  name='subir_orden_pista'),
    path('musica/<int:pk>/bajar/',    views.bajar_orden_pista,  name='bajar_orden_pista'),

    # Cambio 4: Editar perfil del paciente
    path('perfil/editar/', views.editar_perfil_paciente, name='editar_perfil_paciente'),

    # HU-027: Recordatorio diario por correo
    path('recordatorio/', views.configurar_recordatorio, name='configurar_recordatorio'),

    # HU-026: Responder pregunta diaria
    path('pregunta-diaria/', views.responder_pregunta_diaria, name='responder_pregunta_diaria'),
    path('pregunta-diaria/historial/', views.historial_pregunta_diaria, name='historial_pregunta_diaria'),

    # HU-028: Ejercicio de respiración guiada
    path('bienestar/respiracion/', views.respiracion_guiada, name='respiracion_guiada'),

    # HU-022: Registrar estado de ánimo diario
    path('animo/', views.registrar_animo, name='registrar_animo'),

    # HU-024: Visualizar calendario emocional
    path('animo/calendario/', views.calendario_animo, name='calendario_animo'),
    path('animo/calendario/<int:paciente_id>/', views.calendario_animo, name='calendario_animo_paciente'),

    # HU-005: recuperacion de contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='cuentas/password_reset.html',
        email_template_name='cuentas/password_reset_email.html',
        success_url='/cuentas/password_reset_done/'
    ), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='cuentas/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='cuentas/password_reset_confirm.html',
        success_url='/cuentas/reset_complete/'
    ), name='password_reset_confirm'),
    path('reset_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='cuentas/password_reset_complete.html'
    ), name='password_reset_complete'),
]
