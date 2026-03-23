from django import forms


class ImportarExcelOTForm(forms.Form):
    archivo = forms.FileField(
        label="Archivo Excel",
        help_text="Sube un archivo .xlsx con el listado de órdenes de trabajo."
    )

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]

        if not archivo.name.endswith(".xlsx"):
            raise forms.ValidationError("Solo se permiten archivos .xlsx")

        return archivo