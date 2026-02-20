from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Usuario, Auditoria
from .forms import UsuarioForm

# FUNCIONES AUXILIARES

def es_admin(user):
    return user.is_superuser or getattr(user, 'rol', None) in ['admin', 'admin_general']


def es_admin_general(user):
    return user.is_superuser or getattr(user, 'rol', None) == 'admin_general'


# DASHBOARD PRINCIPAL

@login_required
def dashboard(request):

    if es_admin_general(request.user):
        return render(request, 'usuarios/dashboard_admin_general.html')

    elif getattr(request.user, 'rol', None) == 'admin':
        return render(request, 'usuarios/dashboard_admin.html')

    else:
        return render(request, 'usuarios/dashboard_usuario.html')


# LISTAR USUARIOS

@login_required
def lista_usuarios(request):

    if not es_admin(request.user):
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})


# CREAR USUARIO

@login_required
def crear_usuario(request):

    if not es_admin(request.user):
        return HttpResponseForbidden("No tienes permiso para crear usuarios.")

    form = UsuarioForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():

            # admin normal SOLO puede crear usuarios normales
            if not es_admin_general(request.user):
                if form.cleaned_data['rol'] != 'usuario':
                    messages.error(request, "No tienes permiso para crear este tipo de usuario.")
                    return redirect('lista_usuarios')

            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password1'])
            usuario.save()

            Auditoria.objects.create(
                usuario=request.user,
                accion=f"Creó el usuario {usuario.username}"
            )

            messages.success(request, "Usuario creado correctamente.")
            return redirect('lista_usuarios')

    return render(request, 'usuarios/crear_usuario.html', {'form': form})

# EDITAR USUARIO

@login_required
def editar_usuario(request, id):

    if not es_admin(request.user):
        return HttpResponseForbidden("No tienes permiso para editar usuarios.")

    usuario = get_object_or_404(Usuario, id=id)

    # Permisos de edición
    if es_admin_general(request.user):
        pass

    elif request.user.rol == 'admin':
        if usuario.rol != 'usuario':
            return HttpResponseForbidden("No puedes editar este tipo de usuario.")

    else:
        return HttpResponseForbidden("No tienes permiso para editar usuarios.")

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)

        if form.is_valid():

            # Admin normal NO puede cambiar roles
            if not es_admin_general(request.user):
                if form.cleaned_data['rol'] != 'usuario':
                    messages.error(request, "No tienes permiso para asignar ese rol.")
                    return redirect('lista_usuarios')

            # Evitar que alguien se quite privilegios accidentalmente
            if request.user == usuario and not es_admin_general(request.user):
                if form.cleaned_data['rol'] != request.user.rol:
                    messages.error(request, "No puedes cambiar tu propio rol.")
                    return redirect('lista_usuarios')

            usuario = form.save(commit=False)

            password1 = form.cleaned_data.get('password1')
            if password1:
                usuario.set_password(password1)

            usuario.save()

            Auditoria.objects.create(
                usuario=request.user,
                accion=f"Editó el usuario {usuario.username}"
            )

            messages.success(request, "Usuario actualizado correctamente.")
            return redirect('lista_usuarios')

    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'usuarios/editar_usuario.html', {'form': form})


# ELIMINAR USUARIO

@login_required
@require_POST
def eliminar_usuario(request, id):

    if not es_admin(request.user):
        return HttpResponseForbidden("No tienes permiso para eliminar usuarios.")

    usuario = get_object_or_404(Usuario, id=id)

    # Evitar auto-eliminación
    if usuario == request.user:
        messages.error(request, "No puedes eliminar tu propio usuario.")
        return redirect('lista_usuarios')

    username_eliminado = usuario.username

    # Permisos
    if es_admin_general(request.user):

        usuario.delete()

        Auditoria.objects.create(
            usuario=request.user,
            accion=f"Borró el usuario {username_eliminado}"
        )

        messages.success(request, "Usuario eliminado correctamente.")

    elif request.user.rol == 'admin':

        if usuario.rol == 'usuario':

            usuario.delete()

            Auditoria.objects.create(
                usuario=request.user,
                accion=f"Borró el usuario {username_eliminado}"
            )

            messages.success(request, "Usuario eliminado correctamente.")

        else:
            return HttpResponseForbidden("No puedes eliminar este tipo de usuario.")

    else:
        return HttpResponseForbidden("No tienes permiso para eliminar usuarios.")

    return redirect('lista_usuarios')