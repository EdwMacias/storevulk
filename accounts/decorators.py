from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_admin():
            messages.error(request, 'Solo los administradores pueden acceder a esta página.')
            return redirect('main:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                messages.error(request, 'No tienes permisos para acceder a esta página.')
                return redirect('main:dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator