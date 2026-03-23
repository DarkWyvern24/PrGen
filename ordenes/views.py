import os
import tempfile

from django.contrib import messages
from django.core.management import call_command
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ImportarExcelOTForm
from .models import OrdenTrabajo
from collections import OrderedDict
from django.db.models import Count



def reporte_ot(request):
    total_ot = OrdenTrabajo.objects.count()

    estados_qs = (
        OrdenTrabajo.objects
        .values("estado")
        .annotate(total=Count("numero"))
        .order_by("estado")
    )

    urgencias_qs = (
        OrdenTrabajo.objects
        .values("nivel_urgencia")
        .annotate(total=Count("numero"))
        .order_by("nivel_urgencia")
    )

    estados_labels = []
    estados_data = []

    for item in estados_qs:
        nombre = item["estado"].strip() if item["estado"] else "Sin estado"
        estados_labels.append(nombre)
        estados_data.append(item["total"])

    urgencias_labels = []
    urgencias_data = []

    for item in urgencias_qs:
        nombre = item["nivel_urgencia"].strip() if item["nivel_urgencia"] else "Sin urgencia"
        urgencias_labels.append(nombre)
        urgencias_data.append(item["total"])

    ultimas_ot = OrdenTrabajo.objects.all().order_by("-fecha", "-numero")[:10]

    context = {
        "total_ot": total_ot,
        "estados_labels": estados_labels,
        "estados_data": estados_data,
        "urgencias_labels": urgencias_labels,
        "urgencias_data": urgencias_data,
        "ultimas_ot": ultimas_ot,
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


# ===============================
# IMPORTAR EXCEL
# ===============================
def importar_ot_excel_view(request):
    if request.method == "POST":
        form = ImportarExcelOTForm(request.POST, request.FILES)

        if form.is_valid():
            archivo = form.cleaned_data["archivo"]

            # Guardar temporalmente el archivo
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
                for chunk in archivo.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name

            try:
                # Llamar al comando de importación
                call_command("importar_ot_excel", ruta=temp_path)

                messages.success(request, "Archivo importado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al importar el archivo: {e}")
            finally:
                # Eliminar archivo temporal
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            return redirect("ordenes:listado_ot")

    else:
        form = ImportarExcelOTForm()

    return render(request, "ordenes/importar_ot_excel.html", {"form": form})