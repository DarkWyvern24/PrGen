from django import forms
from .models import Usuario


class UsuarioForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=False
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'rol']
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "rol": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        self.es_edicion = kwargs.pop("es_edicion", False)
        super().__init__(*args, **kwargs)

        if not self.es_edicion:
            self.fields["password1"].required = True
            self.fields["password2"].required = True

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if not self.es_edicion and (not password1 or not password2):
            raise forms.ValidationError("Debes ingresar y confirmar la contraseña.")

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden")

        return cleaned_data