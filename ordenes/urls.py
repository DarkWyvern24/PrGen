from django.urls import path
from . import views

app_name = "ordenes"

urlpatterns = [
    path("", views.listado_ot, name="listado_ot"),
    path("importar/", views.importar_ot_excel_view, name="importar_ot_excel"),
    path("reporte/", views.reporte_ot, name="reporte_ot"),
    path("<str:pk>/", views.detalle_ot, name="detalle_ot"),
]