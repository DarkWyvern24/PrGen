from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.lista_usuarios, name='lista_usuarios'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('desactivar/<int:id>/', views.confirmar_eliminar_usuario, name='confirmar_eliminar_usuario'),
    path('eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
    path('admin-general/', views.dashboard_admin_general, name='dashboard_admin_general'),
    path('admin/', views.dashboard_admin, name='dashboard_admin'),
    path('usuario/', views.dashboard_usuario, name='dashboard_usuario'),
    path('jefe-taller/', views.dashboard_jefe_taller, name='dashboard_jefe_taller'),
]