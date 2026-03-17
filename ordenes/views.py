from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

from .models import OrdenTrabajo, Solicitante, Cliente, Responsable
from .forms import OrdenTrabajoForm
from datetime import date
from django.db.models import Exists, OuterRef, Q
from usuarios.decorators import admin_required
from asignaciones.models import AsignacionOT


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


def calcular_porcentaje_esperado(fecha_inicio, fecha_entrega, hoy=None):
    """
    Ejemplo:
    inicio = 10/03
    entrega = 14/03
    hoy = 12/03
    resultado = 40%
    """
    if not fecha_inicio or not fecha_entrega:
        return 0

    if hoy is None:
        hoy = date.today()

    # Si fecha_inicio viene como DateTimeField
    if hasattr(fecha_inicio, "date"):
        fecha_inicio = fecha_inicio.date()

    if hasattr(fecha_entrega, "date"):
        fecha_entrega = fecha_entrega.date()

    if hoy <= fecha_inicio:
        return 0

    if hoy >= fecha_entrega:
        return 100

    total_dias = (fecha_entrega - fecha_inicio).days + 1
    dias_transcurridos = (hoy - fecha_inicio).days

    if total_dias <= 0:
        return 100

    porcentaje = round((dias_transcurridos / total_dias) * 100)
    return max(0, min(100, porcentaje))


def obtener_estado_avance(real, esperado, finalizada=False):
    """
    rojo: atrasado
    amarillo: similar
    verde: terminado o adelantado
    """
    if finalizada or real >= 100:
        return "verde"

    if real > esperado:
        return "verde"

    if abs(real - esperado) <= 5:
        return "amarillo"

    return "rojo"


@admin_required
def reporte_ot(request):
    hoy = date.today()

    asignaciones_subquery = AsignacionOT.objects.filter(
        orden_trabajo=OuterRef("pk")
    )

    ots = OrdenTrabajo.objects.annotate(
        tiene_asignacion=Exists(asignaciones_subquery)
    ).order_by("-idOT")

    total_ot = ots.count()

    no_iniciadas = ots.filter(
        Q(tiene_asignacion=False) |
        Q(tiene_asignacion=True, porcentajeAvance=0)
    )

    en_proceso = ots.filter(
        Q(tiene_asignacion=True) &
        Q(porcentajeAvance__gt=0) &
        Q(porcentajeAvance__lt=100)
    ).exclude(
        estadoOT__nombreEstado__iexact="entregada"
    )

    finalizadas = ots.filter(
        Q(porcentajeAvance__gte=100) |
        Q(estadoOT__nombreEstado__iexact="entregada")
    )

    listado_en_proceso = []

    for ot in en_proceso:
        porcentaje_real = ot.porcentajeAvance or 0
        fecha_inicio = ot.fechaHoraSolicitud
        fecha_entrega = ot.fechaEntregaTrabajo
        estado_nombre = ot.estadoOT.nombreEstado.lower() if ot.estadoOT else ""

        porcentaje_esperado = calcular_porcentaje_esperado(
            fecha_inicio=fecha_inicio,
            fecha_entrega=fecha_entrega,
            hoy=hoy
        )

        finalizada_flag = porcentaje_real >= 100 or estado_nombre == "entregada"

        semaforo = obtener_estado_avance(
            real=porcentaje_real,
            esperado=porcentaje_esperado,
            finalizada=finalizada_flag
        )

        listado_en_proceso.append({
            "ot": ot,
            "numero_ot": ot.idOT,
            "porcentaje_real": round(porcentaje_real, 2),
            "porcentaje_esperado": porcentaje_esperado,
            "semaforo": semaforo,
        })

    context = {
        "total_ot": total_ot,
        "total_no_iniciadas": no_iniciadas.count(),
        "total_en_proceso": en_proceso.count(),
        "total_finalizadas": finalizadas.count(),
        "listado_en_proceso": listado_en_proceso,
    }

    return render(request, "ordenes/reporte_ot.html", context)