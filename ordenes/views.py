from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

from .models import OrdenTrabajo, Solicitante, Cliente, Responsable
from .forms import OrdenTrabajoForm


def es_admin(user):
    return user.rol in ['admin', 'admin_general']


# 🔹 LISTAR
@login_required
def lista_ot(request):
    ordenes = OrdenTrabajo.objects.all()
    return render(request, 'ordenes/lista_ot.html', {'ordenes': ordenes})


# 🔹 CREAR
@login_required
def crear_ot(request):

    if not es_admin(request.user):
        messages.error(request, "No tienes permiso para crear órdenes.")
        return redirect('ordenes:lista_ot')

    if request.method == 'POST':
        form = OrdenTrabajoForm(request.POST)

        tipo_solicitante = request.POST.get('tipo_solicitante')
        tipo_cliente = request.POST.get('tipo_cliente')
        tipo_responsable = request.POST.get('tipo_responsable')

        # Quitar obligatoriedad si es nuevo
        if tipo_solicitante == 'nuevo':
            form.fields['solicitante'].required = False
        if tipo_cliente == 'nuevo':
            form.fields['cliente'].required = False
        if tipo_responsable == 'nuevo':
            form.fields['responsable'].required = False

        if form.is_valid():
            ot = form.save(commit=False)

            # ==========================
            # SOLICITANTE
            # ==========================
            if tipo_solicitante == 'nuevo':

                rut = request.POST.get('nuevo_rut_solicitante')
                nombre = request.POST.get('nuevo_nombre_solicitante')
                mail = request.POST.get('nuevo_mail_solicitante')
                telefono = request.POST.get('nuevo_telefono_solicitante')

                if not all([rut, nombre, mail, telefono]):
                    messages.error(request, "Todos los campos del nuevo solicitante son obligatorios.")
                    return render(request, 'ordenes/crear_ot.html', {'form': form})

                if Solicitante.objects.filter(rutSolicitante=rut).exists():
                    messages.error(request, "El solicitante ya existe.")
                    return render(request, 'ordenes/crear_ot.html', {'form': form})

                nuevo_solicitante = Solicitante.objects.create(
                    rutSolicitante=rut,
                    nombreSolicitante=nombre,
                    mailSolicitante=mail,
                    telefonoSolicitante=telefono
                )

                ot.solicitante = nuevo_solicitante

            # ==========================
            # CLIENTE
            # ==========================
            if tipo_cliente == 'nuevo':

                rut = request.POST.get('nuevo_rut_cliente')
                nombre = request.POST.get('nuevo_nombre_cliente')
                mail = request.POST.get('nuevo_mail_cliente')
                telefono = request.POST.get('nuevo_telefono_cliente')

                if not all([rut, nombre, mail, telefono]):
                    messages.error(request, "Todos los campos del nuevo cliente son obligatorios.")
                    return render(request, 'ordenes/crear_ot.html', {'form': form})

                if Cliente.objects.filter(rutCliente=rut).exists():
                    messages.error(request, "El cliente ya existe.")
                    return render(request, 'ordenes/crear_ot.html', {'form': form})

                nuevo_cliente = Cliente.objects.create(
                    rutCliente=rut,
                    nombreCliente=nombre,
                    mailCliente=mail,
                    telefonoCliente=telefono
                )

                ot.cliente = nuevo_cliente

            # ==========================
            # RESPONSABLE
            # ==========================
            if tipo_responsable == 'nuevo':

                rut = request.POST.get('nuevo_rut_responsable')
                nombre = request.POST.get('nuevo_nombre_responsable')
                mail = request.POST.get('nuevo_mail_responsable')
                telefono = request.POST.get('nuevo_telefono_responsable')

                if not all([rut, nombre, mail, telefono]):
                    messages.error(request, "Todos los campos del nuevo responsable son obligatorios.")
                    return render(request, 'ordenes/crear_ot.html', {'form': form})

                if Responsable.objects.filter(rutResponsable=rut).exists():
                    messages.error(request, "El responsable ya existe.")
                    return render(request, 'ordenes/crear_ot.html', {'form': form})

                nuevo_responsable = Responsable.objects.create(
                    rutResponsable=rut,
                    nombreResponsable=nombre,
                    mailResponsable=mail,
                    telefonoResponsable=telefono
                )

                ot.responsable = nuevo_responsable

            ot.save()
            messages.success(request, "Orden creada correctamente.")
            return redirect('ordenes:lista_ot')

    else:
        form = OrdenTrabajoForm()

    return render(request, 'ordenes/crear_ot.html', {'form': form})


# 🔹 EDITAR
@login_required
def editar_ot(request, id):

    if not es_admin(request.user):
        messages.error(request, "No tienes permiso para editar órdenes.")
        return redirect('ordenes:lista_ot')

    orden = get_object_or_404(OrdenTrabajo, idOT=id)

    if request.method == 'POST':
        form = OrdenTrabajoForm(request.POST, instance=orden)
        if form.is_valid():
            form.save()
            messages.success(request, "Orden actualizada correctamente.")
            return redirect('ordenes:lista_ot')
    else:
        form = OrdenTrabajoForm(instance=orden)

    return render(request, 'ordenes/editar_ot.html', {'form': form})


# 🔹 ELIMINAR
@login_required
def eliminar_ot(request, id):

    if not es_admin(request.user):
        messages.error(request, "No tienes permiso para eliminar órdenes.")
        return redirect('ordenes:lista_ot')

    orden = get_object_or_404(OrdenTrabajo, idOT=id)

    if request.method == 'POST':
        orden.delete()
        messages.success(request, "Orden eliminada correctamente.")

    return redirect('ordenes:lista_ot')