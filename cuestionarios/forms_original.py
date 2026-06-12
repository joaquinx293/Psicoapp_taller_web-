from django import forms
from .models import Cuestionario, Pregunta


class CuestionarioForm(forms.ModelForm):
    """HU-011: crear/editar datos del cuestionario"""

    class Meta:
        model = Cuestionario
        fields = ['nombre', 'descripcion', 'escala']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'escala': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'nombre': 'Nombre del cuestionario',
            'descripcion': 'Descripcion',
            'escala': 'Tipo de escala de respuesta',
        }


class PreguntaForm(forms.ModelForm):
    """HU-012, HU-013: agregar/editar pregunta"""

    class Meta:
        model = Pregunta
        fields = ['texto', 'peso']
        widgets = {
            'texto': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 250}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }
        labels = {
            'texto': 'Texto de la pregunta',
            'peso': 'Peso en el puntaje (1 a 10)',
        }