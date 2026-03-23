from django.contrib import admin
from .models import AsignacionOT


@admin.register(AsignacionOT)
class AsignacionOTAdmin(admin.ModelAdmin):
    list_display = ("id", "orden_trabajo", "fecha_asignacion", "fecha_entrega", "porcentaje_trabajo", "entregado")
    list_filter = ("entregado", "porcentaje_trabajo")
    search_fields = ("orden_trabajo__numero", "referencia")