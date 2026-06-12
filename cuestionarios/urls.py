from django.urls import path
from . import views

app_name = 'cuestionarios'

urlpatterns = [
    # Especialista
    path('', views.listado_cuestionarios, name='listado'),
    path('crear/', views.crear_cuestionario, name='crear'),
    path('<int:pk>/', views.detalle_cuestionario, name='detalle'),
    path('<int:pk>/enviar-revision/', views.enviar_a_revision, name='enviar_revision'),
    path('<int:pk>/importar-pregunta/', views.importar_pregunta, name='importar_pregunta'),
    path('asignar/<int:paciente_pk>/', views.asignar_cuestionario, name='asignar_cuestionario'),
    path('pregunta/<int:pk>/editar/', views.editar_pregunta, name='editar_pregunta'),
    path('pregunta/<int:pk>/desactivar/', views.desactivar_pregunta, name='desactivar_pregunta'),
    path('pregunta/<int:pk>/eliminar/', views.eliminar_pregunta, name='eliminar_pregunta'),

    # Paciente
    path('mis-cuestionarios/', views.mis_cuestionarios_paciente, name='mis_cuestionarios_paciente'),
    path('<int:pk>/responder/', views.responder_cuestionario, name='responder_cuestionario'),

    # Especialista ve respuestas de paciente
    path('paciente/<int:paciente_pk>/respuestas/', views.ver_respuestas_paciente, name='ver_respuestas_paciente'),
]
