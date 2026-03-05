from django import forms
from .models import Trabajador


class TrabajadorForm(forms.ModelForm):

    class Meta:
        model = Trabajador
        fields = ['nombre', 'cargo', 'activo']

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'cargo': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }