from django.urls import path
from . import views

app_name = 'mantenedores'

urlpatterns = [
    path('terminos/', views.gestionar_terminos, name='terminos'),
]
