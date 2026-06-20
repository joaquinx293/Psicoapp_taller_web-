from django.urls import path
from . import views

app_name = 'cuestionarios'

urlpatterns = [
    path('', views.listado_cuestionarios, name='listado'),
    path('crear/', views.crear_cuestionario, name='crear'),
    path('<int:pk>/', views.detalle_cuestionario, name='detalle'),
    path('<int:pk>/enviar-revision/', views.enviar_a_revision, name='enviar_revision'),
    path('<int:pk>/importar-pregunta/', views.importar_pregunta, name='importar_pregunta'),
    path('asignar/<int:paciente_pk>/', views.asignar_cuestionario, name='asignar_cuestionario'),
    path('asignar-pendiente/<int:invitacion_pk>/', views.asignar_pendiente, name='asignar_pendiente'),
    path('pregunta/<int:pk>/editar/', views.editar_pregunta, name='editar_pregunta'),
    path('pregunta/<int:pk>/desactivar/', views.desactivar_pregunta, name='desactivar_pregunta'),
    path('pregunta/<int:pk>/eliminar/', views.eliminar_pregunta, name='eliminar_pregunta'),
    path('crear-gad7/', views.crear_gad7, name='crear_gad7'),
    path('mis-cuestionarios/', views.mis_cuestionarios_paciente, name='mis_cuestionarios_paciente'),
    path('<int:pk>/responder/', views.responder_cuestionario, name='responder_cuestionario'),
    path('resultado/<int:respuesta_pk>/', views.resultado_cuestionario, name='resultado_cuestionario'),
    path('paciente/<int:paciente_pk>/respuestas/', views.ver_respuestas_paciente, name='ver_respuestas_paciente'),

    # Admin: revisar cuestionario enviado a revision
    path('revisar/<int:pk>/', views.revisar_cuestionario, name='revisar_cuestionario'),

    # Especialista: explorar y copiar cuestionarios publicos
    path('publicos/', views.cuestionarios_publicos, name='cuestionarios_publicos'),
    path('publicos/<int:pk>/copiar/', views.cuestionarios_publicos, name='copiar_cuestionario_publico'),

    # Reordenar preguntas via drag & drop
    path('<int:pk>/reordenar/', views.reordenar_preguntas, name='reordenar_preguntas'),
    path('<int:pk>/reordenar/guardar/', views.guardar_orden, name='guardar_orden'),
]
