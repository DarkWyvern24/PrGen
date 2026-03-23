from django.contrib import admin
from .models import OrdenTrabajo


@admin.register(OrdenTrabajo)
class OrdenTrabajoAdmin(admin.ModelAdmin):
    list_display = (
        "numero",
        "fecha",
        "numero_cotizacion",
        "cliente",
        "referencia",
        "atencion",
        "responsable",
        "estado",
        "nivel_urgencia",
    )
    search_fields = (
        "numero",
        "numero_cotizacion",
        "cliente",
        "referencia",
        "atencion",
        "responsable",
        "estado",
        "nivel_urgencia",
    )
    list_filter = ("estado", "nivel_urgencia", "fecha")
    ordering = ("-numero",)