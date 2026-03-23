from django.db import models
from django.core.validators import RegexValidator


validador_8_digitos = RegexValidator(
    regex=r"^\d{8}$",
    message="Este campo debe contener exactamente 8 dígitos."
)


class OrdenTrabajo(models.Model):
    numero = models.CharField(
        primary_key=True,
        max_length=8,
        validators=[validador_8_digitos]
    )
    fecha = models.DateField(null=True, blank=True)
    numero_cotizacion = models.CharField(
        max_length=8,
        blank=True,
        validators=[validador_8_digitos]
    )
    cliente = models.CharField(max_length=255, blank=True)
    referencia = models.CharField(max_length=255, blank=True)
    atencion = models.CharField(max_length=255, blank=True)
    responsable = models.CharField(max_length=255, blank=True)
    estado = models.CharField(max_length=100, blank=True)
    nivel_urgencia = models.CharField(max_length=100, blank=True)
    fecha_entrega = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "ordentrabajo"
        verbose_name = "Orden de Trabajo"
        verbose_name_plural = "Órdenes de Trabajo"
        ordering = ["-numero"]

    def __str__(self):
        return f"OT {self.numero}"