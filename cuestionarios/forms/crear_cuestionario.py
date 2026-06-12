# HU-011: Crear cuestionario personalizado
from django import forms
from ..models import Cuestionario


class CuestionarioForm(forms.ModelForm):

    class Meta:
        model = Cuestionario
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'nombre': 'Nombre del cuestionario',
            'descripcion': 'Descripcion',
        }
