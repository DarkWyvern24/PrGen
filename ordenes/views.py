import os
from datetime import date

from django.contrib import messages
from django.core.management import call_command
from django.db.models import Q, Exists, OuterRef, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from .models import OrdenTrabajo
from asignaciones.models import AsignacionOT
from usuarios.decorators import admin_required
from django.contrib.auth.decorators import login_required
from django.conf import settings

@admin_required
def reporte_ot(request):
    hoy = date.today()

    asignaciones_subquery = AsignacionOT.objects.filter(
        orden_trabajo=OuterRef("pk")
    )

    asignaciones_prefetch = Prefetch(
        "asignaciones",
        queryset=AsignacionOT.objects.prefetch_related("trabajadores").order_by("-fecha_asignacion", "-id"),
        to_attr="asignaciones_ordenadas"
    )

    ots = (
        OrdenTrabajo.objects
        .annotate(tiene_asignacion=Exists(asignaciones_subquery))
        .prefetch_related(asignaciones_prefetch)
        .order_by("-tiene_asignacion", "-fecha", "-numero")
    )

    total_ot = ots.count()
    total_asignadas = ots.filter(tiene_asignacion=True).count()
    total_no_asignadas = total_ot - total_asignadas

    asignaciones_resumen = []
    total_no_iniciadas = 0
    total_en_proceso = 0
    total_finalizadas = 0

    for ot in ots:
        if not ot.tiene_asignacion:
            continue

        asignacion = ot.asignaciones_ordenadas[0] if getattr(ot, "asignaciones_ordenadas", []) else None
        if not asignacion:
            continue

        porcentaje_real = asignacion.porcentaje_trabajo or 0

        fecha_inicio = ot.fecha or asignacion.fecha_asignacion #no usar fecha de asignacion, solo la de la ot..
        fecha_fin = asignacion.fecha_entrega or ot.fecha_entrega

        porcentaje_esperado = 0
        semaforo = "gris"
        estado_seguimiento = "Sin fecha"

        if asignacion.entregado or porcentaje_real >= 100:
            porcentaje_esperado = 100
            semaforo = "verde"
            estado_seguimiento = "Finalizada"
            total_finalizadas += 1

        elif fecha_inicio and fecha_fin:
            dias_totales = (fecha_fin - fecha_inicio).days
            dias_transcurridos = (hoy - fecha_inicio).days

            if dias_totales <= 0:
                porcentaje_esperado = 100 if hoy >= fecha_fin else 0
            else:
                porcentaje_esperado = round((dias_transcurridos / dias_totales) * 100)
                porcentaje_esperado = max(0, min(100, porcentaje_esperado))

            diferencia = porcentaje_real - porcentaje_esperado

            if porcentaje_real == 0:
                semaforo = "negro"
                estado_seguimiento = "No iniciada"
                total_no_iniciadas += 1
            elif porcentaje_real >= 100:
                semaforo = "verde"
                estado_seguimiento = "Finalizada"
                total_finalizadas += 1
            elif diferencia < -10:
                semaforo = "rojo"
                estado_seguimiento = "Atrasado"
                total_en_proceso += 1
            elif diferencia <= 10:
                semaforo = "amarillo"
                estado_seguimiento = "En proceso"
                total_en_proceso += 1
            else:
                semaforo = "verde"
                estado_seguimiento = "En proceso"
                total_en_proceso += 1

        else:
            if porcentaje_real == 0:
                semaforo = "rojo"
                estado_seguimiento = "No iniciada"
                total_no_iniciadas += 1
            elif porcentaje_real >= 100:
                semaforo = "verde"
                estado_seguimiento = "Finalizada"
                total_finalizadas += 1
            else:
                semaforo = "amarillo"
                estado_seguimiento = "En proceso"
                total_en_proceso += 1

        trabajadores = ", ".join(
            [trabajador.nombre for trabajador in asignacion.trabajadores.all()]
        ) or "-"

        asignaciones_resumen.append({
            "numero_ot": ot.numero,
            "cliente": ot.cliente,
            "referencia": asignacion.referencia or ot.referencia,
            "trabajadores": trabajadores,
            "fecha_asignacion": asignacion.fecha_asignacion,
            "fecha_entrega": fecha_fin,
            "porcentaje_real": porcentaje_real,
            "porcentaje_esperado": porcentaje_esperado,
            "estado_seguimiento": estado_seguimiento,
            "semaforo": semaforo,
        })

    ots_no_asignadas = (
        ots.filter(tiene_asignacion=False)
        .order_by("-fecha", "-numero")
    )

    context = {
        "total_ot": total_ot,
        "total_asignadas": total_asignadas,
        "total_no_asignadas": total_no_asignadas,
        "total_no_iniciadas": total_no_iniciadas,
        "total_en_proceso": total_en_proceso,
        "total_finalizadas": total_finalizadas,
        "asignaciones_resumen": asignaciones_resumen,
        "ots_no_asignadas": ots_no_asignadas,
    }

    return render(request, "ordenes/reporte_ot.html", context)

# ===============================
# LISTADO DE OT
# ===============================
def listado_ot(request):
    query = request.GET.get("q", "").strip()

    ots = OrdenTrabajo.objects.all()

    if query:
        ots = ots.filter(
            Q(numero__icontains=query) |
            Q(cliente__icontains=query) |
            Q(referencia__icontains=query) |
            Q(responsable__icontains=query) |
            Q(estado__icontains=query)
        )

    context = {
        "ots": ots,
        "query": query,
    }
    return render(request, "ordenes/listado_ot.html", context)


# ===============================
# DETALLE DE OT
# ===============================
def detalle_ot(request, pk):
    ot = get_object_or_404(OrdenTrabajo, pk=pk)

    context = {
        "ot": ot
    }
    return render(request, "ordenes/detalle_ot.html", context)

"""
# ===============================
# IMPORTAR EXCEL
# ===============================
def importar_ot_excel_view(request):
    if request.method == "POST":
        form = ImportarExcelOTForm(request.POST, request.FILES)

        if form.is_valid():
            archivo = form.cleaned_data["archivo"]

            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
                for chunk in archivo.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name

            try:
                call_command("importar_ot_excel", ruta=temp_path)
                messages.success(request, "Archivo importado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al importar el archivo: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            return redirect("ordenes:listado_ot")

    else:
        form = ImportarExcelOTForm()

    return render(request, "ordenes/importar_ot_excel.html", {"form": form})"""

@login_required
def actualizar_ot_excel_view(request):
    ruta_excel = os.path.join(settings.BASE_DIR, "sources", "bd.xlsx")

    if not os.path.exists(ruta_excel):
        messages.error(request, f"No se encontró el archivo Excel en: {ruta_excel}")
        return redirect("ordenes:listado_ot")

    try:
        call_command("importar_ot_excel", ruta=ruta_excel)
        messages.success(request, "Órdenes de trabajo actualizadas correctamente.")
    except Exception as e:
        messages.error(request, f"Error al actualizar las OT desde Excel: {e}")

    return redirect("ordenes:listado_ot")