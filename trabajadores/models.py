from django.db import models


class Trabajador(models.Model):

    nombre = models.CharField(max_length=150)

    cargo = models.CharField(max_length=100, blank=True)

    activo = models.BooleanField(default=True)

    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre