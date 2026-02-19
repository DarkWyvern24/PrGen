from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Usuario(AbstractUser):
    ROLES = (
        ('admin_general', 'Admin General'),
        ('admin', "Admin"),
        ('usuario', 'Usuario'),
    )

    rol = models.CharField(max_length=20, choices=ROLES, default='usuario')

    def __str__(self):
        return self.username