from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

class RoleBasedAccessMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return None
        
        path = request.path
        user_role = request.user.role
        
        admin_only_paths = [
            '/admin/',
            '/accounts/admin/',
        ]

        user_restricted_paths = [
            '/accounts/signup/',
        ]

        # Block admin-only paths for regular users
        if user_role == 'user' and any(path.startswith(admin_path) for admin_path in admin_only_paths):
            messages.error(request, 'No tienes permisos para acceder a esta página.')
            return redirect('main:dashboard')

        # Block signup for all users (only accessible through admin panel)
        if path.startswith('/accounts/signup/'):
            messages.warning(request, 'El registro de usuarios solo está disponible para administradores.')
            return redirect('main:dashboard')
        
        return None