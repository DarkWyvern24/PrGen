from django.urls import path
from . import views



app_name = "ordenes"

urlpatterns = [
    path('', views.lista_ot, name='lista_ot'),
    path('crear/', views.crear_ot, name='crear_ot'),
    path('editar/<str:id>/', views.editar_ot, name='editar_ot'),
    path('eliminar/<str:id>/', views.eliminar_ot, name='eliminar_ot'),
    path('reporte/', views.reporte_ot, name='reporte_ot'),
]