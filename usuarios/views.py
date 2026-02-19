from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Usuario
from .forms import UsuarioForm

# Fucnciones auxiliares:
def es_admin(user):
    return user.rol in ['admin', 'admin_general']

def es_admin_general(user):
    return user.rol == 'admin_general'

#Listar usuarios:
@login_required
def lista_usuarios(request):
    if not es_admin(request.user):
        return redirect('home')  # Redirige a una página de inicio o error si no es admin

    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})

#Creación de usuarios:
@login_required
def crear_usuario(request):
    if not es_admin(request.user):
        return redirect('home')

    form = UsuarioForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():

            # 🔒 Evitar que admin normal cree admin o admin_general
            if request.user.rol == 'admin' and form.cleaned_data['rol'] != 'usuario':
                messages.error(request, "No tienes permiso para crear este tipo de usuario.")
                return redirect('lista_usuarios')

            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password1'])
            usuario.save()

            messages.success(request, "Usuario creado correctamente.")
            return redirect('lista_usuarios')

    return render(request, 'usuarios/crear_usuario.html', {'form': form})

#Editar usuario:
@login_required
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    # Validación de permisos
    if request.user.rol == 'admin_general':
        pass
    elif request.user.rol == 'admin' and usuario.rol == 'usuario':
        pass
    else:
        return redirect('lista_usuarios')

    # Evitar que admin normal cambie rol a admin o admin_general
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)

        if form.is_valid():

            if request.user.rol == 'admin' and form.cleaned_data['rol'] != 'usuario':
                messages.error(request, "No tienes permiso para asignar ese rol.")
                return redirect('lista_usuarios')

            usuario = form.save(commit=False)

            password1 = form.cleaned_data.get('password1')

            # Cambiar contraseña solo si se ingresó una nueva
            if password1:
                usuario.set_password(password1)

            usuario.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'usuarios/editar_usuario.html', {'form': form})

#Eliminar usuario:
@login_required
@require_POST
def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    # Evitar auto-eliminación
    if usuario == request.user:
        messages.error(request, "No puedes eliminar tu propio usuario.")
        return redirect('lista_usuarios')

    # Validación de permisos
    if request.user.rol == 'admin_general':
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")

    elif request.user.rol == 'admin' and usuario.rol == 'usuario':
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")

    else:
        messages.error(request, "No tienes permiso para eliminar este usuario.")

    return redirect('lista_usuarios')


