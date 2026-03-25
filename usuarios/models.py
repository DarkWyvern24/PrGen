from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Usuario(AbstractUser):
    ROLES = (
        ('admin_general', 'Admin General'),
        ('admin', 'Administrador'),
        ('jefe_taller', 'Jefe de Taller'),
        ('usuario', 'Usuario'),
    )

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='usuario'
    )

    def __str__(self):
        estado = "Activo" if self.is_active else "Inactivo"
        return f"{self.username} ({estado})"

    def es_admin(self):
        return self.rol in ['admin', 'admin_general']

    def es_admin_general(self):
        return self.rol == 'admin_general'

    def es_jefe_taller(self):
        return self.rol in ['jefe_taller', 'admin', 'admin_general']


class Auditoria(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    accion = models.CharField(max_length=100)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha}"