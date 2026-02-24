from django import forms
from .models import OrdenTrabajo

class OrdenTrabajoForm(forms.ModelForm):

    class Meta:
        model = OrdenTrabajo
        fields = '__all__'
        widgets = {
            'descripcionTrabajo': forms.Textarea(attrs={
                'class': 'form-control',
                'maxlength': '500',
                'rows': 4,
                'id': 'descripcionTrabajo'
            }),
            'esquemaTrabajo': forms.Textarea(attrs={
                'class': 'form-control',
                'maxlength': '1000',
                'rows': 4,
                'id': 'esquemaTrabajo'
            }),
            'porcentajeAvance': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'step': 0.1,
                'id': 'porcentajeAvance'
            }),
            'fechaHoraSolicitud': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'fechaEntregaTrabajo': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'fechaAsignacion': forms.DateInput(attrs={  
                'type': 'date',
                'class': 'form-control'
            }),
            'fechaEntregaPT': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['solicitante'].required = False
        self.fields['cliente'].required = False
        self.fields['responsable'].required = False

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            elif 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'