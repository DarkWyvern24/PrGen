from django.contrib import admin
from django.urls import path, include
from usuarios import views as usuarios_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', auth_views.LoginView.as_view(
        template_name='usuarios/login.html'
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'
    ), name='logout'),

    path('usuarios/', include('usuarios.urls')),

    path('', usuarios_views.dashboard, name='home'),

    path('ordenes/', include('ordenes.urls')),
]