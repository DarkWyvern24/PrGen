from django.db import models
from trabajadores.models import Trabajador
from datetime import datetime


# Create your models here.
class Cliente(models.Model):
    nombreCliente = models.CharField(max_length=250)
    rutCliente = models.CharField(primary_key=True, max_length=12)
    mailCliente = models.CharField(max_length=250)
    telefonoCliente = models.CharField(max_length=12)

    def __str__(self):
        return self.nombreCliente

class Solicitante(models.Model):
    rutSolicitante = models.CharField(primary_key=True, max_length=12)
    nombreSolicitante = models.CharField(max_length=250)
    mailSolicitante = models.EmailField(max_length=250)
    telefonoSolicitante = models.CharField(max_length=12)

    def __str__(self):
        return self.nombreSolicitante

class Responsable(models.Model):
    rutResponsable = models.CharField(primary_key=True, max_length=12)
    nombreResponsable = models.CharField(max_length=250)
    mailResponsable = models.EmailField(max_length=250)
    telefonoResponsable = models.CharField(max_length=12)

    def __str__(self):
        return self.nombreResponsable

class NivelUrgencia(models.Model):
    idNU = models.IntegerField(primary_key=True)
    descripcionNU = models.CharField(max_length=25)

    def __str__(self):
        return self.descripcionNU

class EstadoOT(models.Model):
    idEstado = models.IntegerField(primary_key=True)
    nombreEstado = models.CharField(max_length=25)

    def __str__(self):
        return self.nombreEstado


class Trabajador(models.Model):
    rutTrabajador = models.CharField(primary_key=True, max_length=12)
    nombreTrabajador = models.CharField(max_length=250)
    telefonoTrabajador = models.CharField(max_length=12, blank=True, null=True)
    mailTrabajador = models.EmailField(max_length=250, blank=True, null=True)

    usuario = models.OneToOneField(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombreTrabajador
    
class OrdenTrabajo(models.Model):

    idOT = models.CharField(primary_key=True, max_length=8, editable=False)

    def save(self, *args, **kwargs):

        if not self.idOT:

            year = datetime.now().year

            # buscar última OT del año
            last_ot = OrdenTrabajo.objects.filter(
                idOT__startswith=str(year)
            ).order_by('-idOT').first()

            if last_ot:
                last_number = int(last_ot.idOT[4:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.idOT = f"{year}{new_number:04d}"

        super().save(*args, **kwargs)

    fechaHoraSolicitud = models.DateTimeField()
    fechaEntregaTrabajo = models.DateField()

    numeroCotizacion = models.CharField(max_length=20)
    referencia = models.CharField(max_length=255)

    descripcionTrabajo = models.CharField(max_length=500)

    porcentajeAvance = models.FloatField()

    fechaAsignacion = models.DateField()
    fechaEntregaPT = models.DateField()

    solicitante = models.ForeignKey(Solicitante, on_delete=models.CASCADE)
    responsable = models.ForeignKey(Responsable, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    nivelUrgencia = models.ForeignKey(NivelUrgencia, on_delete=models.CASCADE)
    estadoOT = models.ForeignKey(EstadoOT, on_delete=models.CASCADE)

    trabajadores = models.ManyToManyField(
    Trabajador,
    blank=True,
    related_name="ordenes"
    )

    def __str__(self):
        return f"OT {self.idOT} - {self.descripcionTrabajo}"

class ControlCalidad(models.Model):
    idCC = models.AutoField(primary_key=True)
    aprobado = models.CharField(max_length=2)
    observaciones = models.CharField(max_length=500)
    fechaRevision = models.DateField()

    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE)

    def __str__(self):
        return f"Control Calidad OT {self.orden.idOT} - Aprobado: {self.aprobado}"
