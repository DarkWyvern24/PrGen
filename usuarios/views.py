from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Usuario, Auditoria
from .forms import UsuarioForm
from .decorators import admin_required, admin_general_required, no_usuario_required

# FUNCIONES AUXILIARES

def es_admin(user):
    return user.is_superuser or getattr(user, 'rol', None) in ['admin', 'admin_general']


def es_admin_general(user):
    return user.is_superuser or getattr(user, 'rol', None) == 'admin_general'


# DASHBOARD PRINCIPAL

@login_required
def dashboard(request):
    return render(request, 'usuarios/dashboard_general.html')


#DASHBOARD JEFES DE TALLER@login_required
def dashboard_jefe_taller(request):
    if request.user.rol != 'jefe_taller':
        return redirect('usuarios:dashboard_usuario')

    return render(request, 'usuarios/dashboard_jefe_taller.html')


# LISTAR USUARIOS

@login_required
@no_usuario_required
def lista_usuarios(request):
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
                    return redirect('usuarios:lista_usuarios')

            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password1'])
            usuario.save()

            Auditoria.objects.create(
                usuario=request.user,
                accion=f"Creó el usuario {usuario.username}"
            )

            messages.success(request, "Usuario creado correctamente.")
            return redirect('usuarios:lista_usuarios')

    return render(request, 'usuarios/crear_usuario.html', {'form': form})

# EDITAR USUARIO

@login_required
def editar_usuario(request, id):

    if not es_admin(request.user):
        messages.error(request, "No tienes permiso para editar usuarios.")
        return redirect('usuarios:lista_usuarios')

    usuario = get_object_or_404(Usuario, id=id)

    # 🔐 Permisos de edición
    if es_admin_general(request.user):
        pass

    elif request.user.rol == 'admin':
        if usuario.rol != 'usuario':
            messages.error(request, "No puedes editar este tipo de usuario.")
            return redirect('usuarios:lista_usuarios')

    else:
        messages.error(request, "No tienes permiso para editar usuarios.")
        return redirect('usuarios:lista_usuarios')

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)

        if form.is_valid():

            # 🔒 Admin normal NO puede cambiar roles
            if not es_admin_general(request.user):
                if form.cleaned_data['rol'] != 'usuario':
                    messages.error(request, "No tienes permiso para asignar ese rol.")
                    return redirect('usuarios:lista_usuarios')

            # 🔒 Evitar que alguien se quite privilegios accidentalmente
            if request.user == usuario and not es_admin_general(request.user):
                if form.cleaned_data['rol'] != request.user.rol:
                    messages.error(request, "No puedes cambiar tu propio rol.")
                    return redirect('usuarios:lista_usuarios')

            usuario_editado = form.save(commit=False)

            password1 = form.cleaned_data.get('password1')
            if password1:
                usuario_editado.set_password(password1)

            usuario_editado.save()

            Auditoria.objects.create(
                usuario=request.user,
                accion=f"Editó el usuario {usuario_editado.username}"
            )

            messages.success(request, "Usuario actualizado correctamente.")
            return redirect('usuarios:lista_usuarios')

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
        return redirect('usuarios:lista_usuarios')

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

    return redirect('usuarios:lista_usuarios')

# CAMBIO CONTRASEÑA PROPIA

@login_required
def cambiar_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña actualizada correctamente.')

            # 🔥 Redirección según rol
            if request.user.rol == 'admin_general':
                return redirect('usuarios:dashboard_admin_general')
            elif request.user.rol == 'admin':
                return redirect('usuarios:dashboard_admin')
            elif request.user.rol == 'jefe_taller':
                return redirect('usuarios:dashboard_jefe_taller')
            else:
                return redirect('usuarios:dashboard_usuario')

    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'usuarios/cambiar_password.html', {'form': form})

# DASHBOARDS ESPECÍFICOS POR ROL

@login_required
def dashboard_admin_general(request):
    if request.user.rol != 'admin_general':
        return redirect('usuarios:dashboard_usuario')

    return render(request, 'usuarios/dashboard_admin_general.html')


@login_required
def dashboard_admin(request):
    if request.user.rol != 'admin':
        return redirect('usuarios:dashboard_usuario')

    return render(request, 'usuarios/dashboard_admin.html')


@login_required
def dashboard_usuario(request):
    return render(request, 'usuarios/dashboard_usuario.html')