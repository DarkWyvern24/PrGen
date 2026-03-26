from django.urls import path
from . import views

app_name = "trabajadores"

urlpatterns = [

    path("", views.lista_trabajadores, name="lista_trabajadores"),

    path("lista/", views.lista_trabajadores, name="lista_trabajadores"),

    path("crear/", views.crear_trabajador, name="crear_trabajador"),

    path("editar/<int:id>/", views.editar_trabajador, name="editar_trabajador"),

    path("actualizar/", views.actualizar_trabajadores, name="actualizar_trabajadores"),

]