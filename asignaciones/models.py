from django.db import models
from ordenes.models import OrdenTrabajo
from trabajadores.models import Trabajador


class AsignacionOT(models.Model):
    orden_trabajo = models.ForeignKey(
        OrdenTrabajo,
        on_delete=models.CASCADE,
        related_name="asignaciones"
    )

    trabajadores = models.ManyToManyField(
        Trabajador,
        related_name="asignaciones"
    )

    fecha_asignacion = models.DateField()

    fecha_entrega = models.DateField(null=True, blank=True)

    descripcion_trabajo = models.TextField(blank=True, default="")

    porcentaje_trabajo = models.IntegerField(
        choices=[(i, f"{i}%") for i in range(0, 101, 10)]
    )

    entregado = models.BooleanField(default=False)

    referencia = models.CharField(max_length=255, blank=True, default="")

    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Asignación OT {self.orden_trabajo.numero}"