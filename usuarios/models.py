from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser
    e incorpora un sistema de roles para control de permisos
    dentro del sistema de gestión de órdenes de trabajo.
    """

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
        return self.username

    # =========================
    # Métodos de control de rol
    # =========================

    def es_admin(self):
        """
        Determina si el usuario posee privilegios administrativos.
        """
        return self.rol in ['admin', 'admin_general']

    def es_admin_general(self):
        """
        Determina si el usuario posee el rol de administrador general.
        """
        return self.rol == 'admin_general'

    def es_jefe_taller(self):
        """
        Determina si el usuario posee permisos de jefe de taller.
        Incluye administradores para evitar bloqueos operativos.
        """
        return self.rol in ['jefe_taller', 'admin', 'admin_general']


class Auditoria(models.Model):
    """
    Registro de auditoría para almacenar acciones relevantes
    realizadas por los usuarios dentro del sistema.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    accion = models.CharField(max_length=100)

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha}"