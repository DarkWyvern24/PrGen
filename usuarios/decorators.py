from django.http import HttpResponseForbidden
from django.shortcuts import redirect   

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.rol in ['admin', 'admin_general']:
            return view_func(request, *args, **kwargs)
        return redirect('home')
    return wrapper

def admin_general_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.rol == 'admin_general':
            return view_func(request, *args, **kwargs)
        return redirect('home')
    return wrapper

def no_usuario_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.rol != 'usuario':
            return view_func(request, *args, **kwargs)
        return redirect('home')
    return wrapper