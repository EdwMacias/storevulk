from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home_view(request):
    """Landing page view"""
    if request.user.is_authenticated:
        return redirect('main:dashboard')
    
    context = {
        'title': 'Bienvenido a Vulkano',
        'description': 'Punto de servicio',
    }
    return render(request, 'main/home.html', context)

@login_required
def dashboard_view(request):
    """Main dashboard view after login"""
    context = {
        'title': 'Panel Principal',
        'user_role': request.user.get_role_display(),
        'is_admin': request.user.is_admin(),
    }
    return render(request, 'main/dashboard.html', context)
