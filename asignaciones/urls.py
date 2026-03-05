from django.urls import path
from . import views

app_name = "asignaciones"

urlpatterns = [
    path("", views.lista_asignaciones, name="lista_asignaciones"),
    path("asignar/", views.asignar_ot, name="asignar_ot"),
    path("editar/<int:pk>/", views.editar_asignacion, name="editar_asignacion"),
    path("eliminar/<int:pk>/", views.eliminar_asignacion, name="eliminar_asignacion"),
]