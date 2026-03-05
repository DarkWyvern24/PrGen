from django.shortcuts import render, redirect, get_object_or_404
from .models import Trabajador
from .forms import TrabajadorForm


def lista_trabajadores(request):

    trabajadores = Trabajador.objects.all()

    return render(
        request,
        "trabajadores/lista.html",
        {"trabajadores": trabajadores}
    )


def crear_trabajador(request):

    if request.method == "POST":
        form = TrabajadorForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("trabajadores:lista_trabajadores")

    else:
        form = TrabajadorForm()

    return render(
        request,
        "trabajadores/crear.html",
        {"form": form}
    )


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
        {"form": form}
    )