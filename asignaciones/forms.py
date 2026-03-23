from django import forms
from .models import AsignacionOT
from ordenes.models import OrdenTrabajo


class AsignacionForm(forms.ModelForm):
    class Meta:
        model = AsignacionOT
        fields = ["orden_trabajo", "porcentaje_trabajo", "entregado"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ordenar por numero, no por idOT
        self.fields["orden_trabajo"].queryset = OrdenTrabajo.objects.all().order_by("-numero")

        # Bootstrap
        self.fields["orden_trabajo"].widget.attrs.update({"class": "form-select"})
        self.fields["porcentaje_trabajo"].widget.attrs.update({"class": "form-select"})
        self.fields["entregado"].widget.attrs.update({"class": "form-check-input"})