from django.urls import path
from . import views

app_name = "ordenes"

urlpatterns = [
    path("", views.listado_ot, name="listado_ot"),
    path("reporte/", views.reporte_ot, name="reporte_ot"),
    path("actualizar/", views.actualizar_ot_excel_view, name="actualizar_ot_excel"),
    path("<str:pk>/", views.detalle_ot, name="detalle_ot"),
    path("<str:pk>/adjuntos/<int:adjunto_id>/editar/", views.editar_adjunto_ot, name="editar_adjunto_ot"),
    path("<str:pk>/adjuntos/<int:adjunto_id>/eliminar/", views.eliminar_adjunto_ot, name="eliminar_adjunto_ot"),
]