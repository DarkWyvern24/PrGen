from django.contrib import admin
from .models import Trabajador


@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "rut",
        "cargo",
        "activo",
    )

    search_fields = (
        "nombre",
        "rut",
        "cargo",
    )

    list_filter = (
        "activo",
        "cargo",
    )