from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Trabajador
from .forms import TrabajadorForm


def lista_trabajadores(request):
    trabajadores = Trabajador.objects.all()

    q = request.GET.get("q", "").strip()
    ordenar = request.GET.get("ordenar", "nombre")
    direccion = request.GET.get("direccion", "asc")

    if q:
        trabajadores = trabajadores.filter(
            Q(nombre__icontains=q) |
            Q(rut__icontains=q) |
            Q(cargo__icontains=q)
        )

    campos_validos = ["id", "nombre", "rut", "cargo", "activo", "creado"]
    if ordenar not in campos_validos:
        ordenar = "nombre"

    if direccion == "desc":
        ordenar_final = f"-{ordenar}"
    else:
        ordenar_final = ordenar

    trabajadores = trabajadores.order_by(ordenar_final)

    return render(
        request,
        "trabajadores/lista.html",
        {
            "trabajadores": trabajadores,
            "q": q,
            "ordenar": request.GET.get("ordenar", "nombre"),
            "direccion": request.GET.get("direccion", "asc"),
        }
    )


def crear_trabajador(request):
    if request.method == "POST":
        form = TrabajadorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("trabajadores:lista_trabajadores")
    else:
        form = TrabajadorForm()

    return render(request, "trabajadores/crear.html", {"form": form})


def editar_trabajador(request, id):
    trabajador = get_object_or_404(Trabajador, id=id)

    if request.method == "POST":
        form = TrabajadorForm(request.POST, instance=trabajador)
        if form.is_valid():
            form.save()
            return redirect("trabajadores:lista_trabajadores")
    else:
        form = TrabajadorForm(instance=trabajador)

    return render(
        request,
        "trabajadores/editar.html",
        {
            "form": form,
            "trabajador": trabajador
        }
    )