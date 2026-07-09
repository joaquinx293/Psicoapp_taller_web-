# HU-011: Crear cuestionario personalizado
from django import forms
from ..models import Cuestionario


class CuestionarioForm(forms.ModelForm):

    class Meta:
        model = Cuestionario
        fields = ['id_cuestionario', 'nombre', 'descripcion']
        widgets = {
            'id_cuestionario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: ANS-001, DEP-002 (debe ser único)',
                'maxlength': 30,
            }),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'id_cuestionario': 'ID del cuestionario',
            'nombre': 'Nombre del cuestionario',
            'descripcion': 'Descripción',
        }
        error_messages = {
            'id_cuestionario': {
                'unique': 'Ya existe un cuestionario con ese ID. Elige uno diferente.',
            }
        }

    def clean_id_cuestionario(self):
        valor = self.cleaned_data.get('id_cuestionario', '').strip().upper()
        if not valor:
            raise forms.ValidationError('El ID del cuestionario es obligatorio.')
        return valor
