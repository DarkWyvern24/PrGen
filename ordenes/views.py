import os
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.db.models import Q, Exists, OuterRef, Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from .models import OrdenTrabajo, AdjuntoOT
from asignaciones.models import AsignacionOT
from usuarios.decorators import admin_required


def puede_editar_comentario(user):
    return user.is_authenticated and getattr(user, "rol", None) in ["admin_general", "admin", "jefe_taller"]


def puede_subir_adjuntos(user):
    return user.is_authenticated and getattr(user, "rol", None) in ["admin_general", "admin", "jefe_taller"]


def puede_editar_adjuntos(user):
    return user.is_authenticated and getattr(user, "rol", None) in ["admin_general", "admin", "jefe_taller"]


def puede_eliminar_adjuntos(user):
    return user.is_authenticated and getattr(user, "rol", None) in ["admin_general", "admin"]


@admin_required
def reporte_ot(request):
    hoy = date.today()
    dias_proximos_vencer = 5

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
        .order_by("-fecha", "-numero")
    )

    total_ot = ots.count()
    total_asignadas = ots.filter(tiene_asignacion=True).count()
    total_no_asignadas = total_ot - total_asignadas

    total_no_iniciadas = 0
    total_en_proceso = 0
    total_finalizadas = 0

    asignaciones_resumen = []
    ots_fuera_plazo = []
    ots_proximas_vencer = []
    ots_no_asignadas = []

    for ot in ots:
        asignaciones = getattr(ot, "asignaciones_ordenadas", [])
        ultima_asignacion = asignaciones[0] if asignaciones else None

        porcentaje_real = 0
        fecha_fin = ot.fecha_entrega
        trabajadores = "-"
        estado_seguimiento = "No asignada"
        semaforo = "secondary"
        porcentaje_esperado = 0
        finalizada = False

        if ultima_asignacion:
            porcentaje_real = ultima_asignacion.porcentaje_trabajo or 0
            fecha_fin = ultima_asignacion.fecha_entrega or ot.fecha_entrega

            nombres_trabajadores = [t.nombre for t in ultima_asignacion.trabajadores.all()]
            trabajadores = ", ".join(nombres_trabajadores) if nombres_trabajadores else "-"

            if ultima_asignacion.entregado or porcentaje_real >= 100 or str(ot.estado).strip().lower() == "entregada":
                finalizada = True
                estado_seguimiento = "Finalizada"
                semaforo = "success"
                porcentaje_esperado = 100
                total_finalizadas += 1

            else:
                fecha_inicio = ot.fecha

                if fecha_inicio and fecha_fin:
                    dias_totales = (fecha_fin - fecha_inicio).days
                    dias_transcurridos = (hoy - fecha_inicio).days

                    if dias_totales <= 0:
                        porcentaje_esperado = 100 if hoy >= fecha_fin else 0
                    else:
                        porcentaje_esperado = round((dias_transcurridos / dias_totales) * 100)
                        porcentaje_esperado = max(0, min(100, porcentaje_esperado))

                if porcentaje_real == 0:
                    estado_seguimiento = "No iniciada"
                    semaforo = "danger"
                    total_no_iniciadas += 1
                else:
                    diferencia = porcentaje_real - porcentaje_esperado

                    if fecha_fin and hoy > fecha_fin:
                        estado_seguimiento = "Fuera de plazo"
                        semaforo = "danger"
                    elif diferencia < -10:
                        estado_seguimiento = "Atrasada"
                        semaforo = "danger"
                    elif diferencia <= 10:
                        estado_seguimiento = "En proceso"
                        semaforo = "warning"
                    else:
                        estado_seguimiento = "Adelantada"
                        semaforo = "success"

                    total_en_proceso += 1

            asignaciones_resumen.append({
                "numero_ot": ot.numero,
                "cliente": ot.cliente,
                "referencia": ot.referencia,
                "trabajadores": trabajadores,
                "fecha_ot": ot.fecha,
                "fecha_entrega": fecha_fin,
                "porcentaje_real": porcentaje_real,
                "porcentaje_esperado": porcentaje_esperado,
                "estado_seguimiento": estado_seguimiento,
                "semaforo": semaforo,
                "responsable": ot.responsable,
                "estado_ot": ot.estado,
            })

        else:
            dias_sin_asignar = None
            if ot.fecha:
                dias_sin_asignar = (hoy - ot.fecha).days

            ots_no_asignadas.append({
                "numero": ot.numero,
                "fecha": ot.fecha,
                "numero_cotizacion": ot.numero_cotizacion,
                "cliente": ot.cliente,
                "referencia": ot.referencia,
                "responsable": ot.responsable,
                "estado": ot.estado,
                "fecha_entrega": ot.fecha_entrega,
                "dias_sin_asignar": dias_sin_asignar,
            })

        if not finalizada and fecha_fin:
            if fecha_fin < hoy:
                dias_atraso = (hoy - fecha_fin).days
                ots_fuera_plazo.append({
                    "numero": ot.numero,
                    "fecha": ot.fecha,
                    "cliente": ot.cliente,
                    "referencia": ot.referencia,
                    "responsable": ot.responsable,
                    "estado": ot.estado,
                    "fecha_entrega": fecha_fin,
                    "dias_atraso": dias_atraso,
                    "porcentaje_real": porcentaje_real,
                    "trabajadores": trabajadores,
                    "tiene_asignacion": bool(ultima_asignacion),
                })
            elif 0 <= (fecha_fin - hoy).days <= dias_proximos_vencer:
                dias_restantes = (fecha_fin - hoy).days
                ots_proximas_vencer.append({
                    "numero": ot.numero,
                    "fecha": ot.fecha,
                    "cliente": ot.cliente,
                    "referencia": ot.referencia,
                    "responsable": ot.responsable,
                    "estado": ot.estado,
                    "fecha_entrega": fecha_fin,
                    "dias_restantes": dias_restantes,
                    "porcentaje_real": porcentaje_real,
                    "trabajadores": trabajadores,
                    "tiene_asignacion": bool(ultima_asignacion),
                })

    asignaciones_resumen.sort(
        key=lambda x: (
            0 if x["semaforo"] == "danger" else 1 if x["semaforo"] == "warning" else 2,
            x["fecha_entrega"] or date.max
        )
    )

    ots_fuera_plazo.sort(key=lambda x: (-x["dias_atraso"], x["fecha_entrega"] or date.max))
    ots_proximas_vencer.sort(key=lambda x: (x["dias_restantes"], x["fecha_entrega"] or date.max))
    ots_no_asignadas.sort(
        key=lambda x: (
            -(x["dias_sin_asignar"] if x["dias_sin_asignar"] is not None else -1),
            x["fecha"] or date.min
        )
    )

    context = {
        "total_ot": total_ot,
        "total_asignadas": total_asignadas,
        "total_no_asignadas": total_no_asignadas,
        "total_no_iniciadas": total_no_iniciadas,
        "total_en_proceso": total_en_proceso,
        "total_finalizadas": total_finalizadas,
        "total_fuera_plazo": len(ots_fuera_plazo),
        "total_proximas_vencer": len(ots_proximas_vencer),
        "dias_proximos_vencer": dias_proximos_vencer,
        "asignaciones_resumen": asignaciones_resumen,
        "ots_fuera_plazo": ots_fuera_plazo,
        "ots_proximas_vencer": ots_proximas_vencer,
        "ots_no_asignadas": ots_no_asignadas,
    }

    return render(request, "ordenes/reporte_ot.html", context)

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


@login_required
def detalle_ot(request, pk):
    ot = get_object_or_404(
        OrdenTrabajo.objects.prefetch_related(
            Prefetch(
                "asignaciones",
                queryset=AsignacionOT.objects.prefetch_related("trabajadores").order_by("-fecha_asignacion", "-id"),
                to_attr="asignaciones_ordenadas"
            ),
            "adjuntos",
        ),
        pk=pk
    )

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "guardar_comentario":
            if not puede_editar_comentario(request.user):
                messages.error(request, "No tienes permiso para editar el comentario.")
                return redirect("ordenes:detalle_ot", pk=ot.pk)

            ot.comentario_detalle = request.POST.get("comentario_detalle", "").strip()
            ot.save()
            messages.success(request, "Comentario actualizado correctamente.")
            return redirect("ordenes:detalle_ot", pk=ot.pk)

        elif accion == "subir_adjunto":
            if not puede_subir_adjuntos(request.user):
                messages.error(request, "No tienes permiso para subir adjuntos.")
                return redirect("ordenes:detalle_ot", pk=ot.pk)

            archivo = request.FILES.get("archivo")
            nombre = request.POST.get("nombre", "").strip()

            if not archivo:
                messages.error(request, "Debes seleccionar un archivo.")
                return redirect("ordenes:detalle_ot", pk=ot.pk)

            AdjuntoOT.objects.create(
                orden_trabajo=ot,
                archivo=archivo,
                nombre=nombre or archivo.name,
                subido_por=request.user
            )
            messages.success(request, "Adjunto subido correctamente.")
            return redirect("ordenes:detalle_ot", pk=ot.pk)

    asignaciones = getattr(ot, "asignaciones_ordenadas", [])
    ultima_asignacion = asignaciones[0] if asignaciones else None

    porcentaje_avance = ultima_asignacion.porcentaje_trabajo if ultima_asignacion else 0

    trabajadores_asignados = []
    for asignacion in asignaciones:
        for trabajador in asignacion.trabajadores.all():
            if trabajador not in trabajadores_asignados:
                trabajadores_asignados.append(trabajador)

    context = {
        "ot": ot,
        "asignaciones": asignaciones,
        "ultima_asignacion": ultima_asignacion,
        "porcentaje_avance": porcentaje_avance,
        "trabajadores_asignados": trabajadores_asignados,
        "adjuntos": ot.adjuntos.all(),
        "puede_editar_comentario": puede_editar_comentario(request.user),
        "puede_subir_adjuntos": puede_subir_adjuntos(request.user),
        "puede_editar_adjuntos": puede_editar_adjuntos(request.user),
        "puede_eliminar_adjuntos": puede_eliminar_adjuntos(request.user),
    }
    return render(request, "ordenes/detalle_ot.html", context)


@login_required
def editar_adjunto_ot(request, pk, adjunto_id):
    ot = get_object_or_404(OrdenTrabajo, pk=pk)
    adjunto = get_object_or_404(AdjuntoOT, id=adjunto_id, orden_trabajo=ot)

    if not puede_editar_adjuntos(request.user):
        messages.error(request, "No tienes permiso para editar adjuntos.")
        return redirect("ordenes:detalle_ot", pk=ot.pk)

    if request.method == "POST":
        nuevo_nombre = request.POST.get("nombre", "").strip()
        if nuevo_nombre:
            adjunto.nombre = nuevo_nombre
            adjunto.save()
            messages.success(request, "Nombre del adjunto actualizado.")
        else:
            messages.error(request, "El nombre no puede quedar vacío.")

    return redirect("ordenes:detalle_ot", pk=ot.pk)


@login_required
def eliminar_adjunto_ot(request, pk, adjunto_id):
    ot = get_object_or_404(OrdenTrabajo, pk=pk)
    adjunto = get_object_or_404(AdjuntoOT, id=adjunto_id, orden_trabajo=ot)

    if not puede_eliminar_adjuntos(request.user):
        messages.error(request, "No tienes permiso para eliminar adjuntos.")
        return redirect("ordenes:detalle_ot", pk=ot.pk)

    if request.method == "POST":
        if adjunto.archivo:
            adjunto.archivo.delete(save=False)
        adjunto.delete()
        messages.success(request, "Adjunto eliminado correctamente.")

    return redirect("ordenes:detalle_ot", pk=ot.pk)


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