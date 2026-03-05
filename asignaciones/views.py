from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.utils import timezone

from .models import AsignacionOT
from .forms import AsignacionForm
from ordenes.models import OrdenTrabajo
from trabajadores.models import Trabajador


def lista_asignaciones(request):
    asignaciones = (
        AsignacionOT.objects
        .select_related("orden_trabajo")
        .prefetch_related("trabajadores")
        .order_by("-id")
    )

    return render(
        request,
        "asignaciones/lista_asignaciones.html",
        {"asignaciones": asignaciones}
    )


def asignar_ot(request):
    # ✅ CAMBIO: nombreTrabajador -> nombre
    trabajadores = Trabajador.objects.filter(activo=True).order_by("nombre")

    if request.method == "POST":
        form = AsignacionForm(request.POST)

        trabajadores_ids = request.POST.getlist("trabajadores_asignados")
        trabajadores_ids = [t for t in trabajadores_ids if str(t).strip() != ""]

        if form.is_valid():
            ot = form.cleaned_data["orden_trabajo"]

            fecha_entrega = ot.fechaEntregaTrabajo
            descripcion = ot.descripcionTrabajo
            fecha_asignacion = timezone.localdate()

            with transaction.atomic():
                asignacion = form.save(commit=False)
                asignacion.fecha_asignacion = fecha_asignacion
                asignacion.fecha_entrega = fecha_entrega
                asignacion.descripcion_trabajo = descripcion
                asignacion.save()

                asignacion.trabajadores.set(trabajadores_ids)

            return redirect("asignaciones:lista_asignaciones")

    else:
        form = AsignacionForm()

    return render(
        request,
        "asignaciones/asignar_ot.html",
        {
            "form": form,
            "trabajadores": trabajadores,
        }
    )


def editar_asignacion(request, pk):
    asignacion = get_object_or_404(AsignacionOT, pk=pk)

    # ✅ CAMBIO: nombreTrabajador -> nombre
    trabajadores = Trabajador.objects.filter(activo=True).order_by("nombre")

    if request.method == "POST":
        form = AsignacionForm(request.POST, instance=asignacion)

        trabajadores_ids = request.POST.getlist("trabajadores_asignados")
        trabajadores_ids = [t for t in trabajadores_ids if str(t).strip() != ""]

        if form.is_valid():
            ot = form.cleaned_data["orden_trabajo"]

            with transaction.atomic():
                obj = form.save(commit=False)
                obj.fecha_entrega = ot.fechaEntregaTrabajo
                obj.descripcion_trabajo = ot.descripcionTrabajo
                obj.save()

                obj.trabajadores.set(trabajadores_ids)

            return redirect("asignaciones:lista_asignaciones")

    else:
        form = AsignacionForm(instance=asignacion)

    return render(
        request,
        "asignaciones/asignar_ot.html",
        {
            "form": form,
            "trabajadores": trabajadores,
            "asignacion": asignacion,
        }
    )


def eliminar_asignacion(request, pk):
    asignacion = get_object_or_404(AsignacionOT, pk=pk)

    if request.method == "POST":
        asignacion.delete()
        return redirect("asignaciones:lista_asignaciones")

    return render(
        request,
        "asignaciones/eliminar_asignacion.html",
        {"asignacion": asignacion}
    )