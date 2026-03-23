from django.db import models


class Trabajador(models.Model):
    nombre = models.CharField(max_length=150)
    rut = models.CharField(max_length=12, unique=True, blank=True)
    cargo = models.CharField(max_length=100, blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        if self.cargo:
            return f"{self.nombre} - {self.cargo}"
        return self.nombre