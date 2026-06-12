# HU-012: Agregar pregunta
# HU-013: Editar pregunta
from django import forms
from ..models import Pregunta


class PreguntaForm(forms.ModelForm):

    class Meta:
        model = Pregunta
        fields = ['texto', 'escala', 'peso']
        widgets = {
            'texto': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 250,
                'placeholder': 'Escribe la pregunta...',
            }),
            'escala': forms.Select(attrs={'class': 'form-select'}),
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
            }),
        }
        labels = {
            'texto': 'Texto de la pregunta',
            'escala': 'Tipo de respuesta',
            'peso': 'Peso en el puntaje (1 a 10)',
        }
