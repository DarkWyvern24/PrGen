from django.http import HttpResponseForbidden

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.rol in ['admin', 'admin_general']:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("No autorizado")
    return wrapper


def admin_general_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.rol == 'admin_general':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("No autorizado")
    return wrapper