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

    # NUEVO
    comentario_detalle = models.TextField(blank=True, default="")

    class Meta:
        db_table = "ordentrabajo"
        verbose_name = "Orden de Trabajo"
        verbose_name_plural = "Órdenes de Trabajo"
        ordering = ["-numero"]

    def __str__(self):
        return f"OT {self.numero}"


def ruta_adjunto_ot(instance, filename):
    return f"adjuntos_ot/{instance.orden_trabajo.numero}/{filename}"


class AdjuntoOT(models.Model):
    orden_trabajo = models.ForeignKey(
        OrdenTrabajo,
        on_delete=models.CASCADE,
        related_name="adjuntos"
    )
    archivo = models.FileField(upload_to=ruta_adjunto_ot)
    nombre = models.CharField(max_length=255, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="adjuntos_ot_subidos"
    )

    class Meta:
        ordering = ["-fecha_subida"]
        verbose_name = "Adjunto OT"
        verbose_name_plural = "Adjuntos OT"

    def __str__(self):
        return self.nombre or self.archivo.name.split("/")[-1]

    def save(self, *args, **kwargs):
        if not self.nombre and self.archivo:
            self.nombre = self.archivo.name.split("/")[-1]
        super().save(*args, **kwargs)