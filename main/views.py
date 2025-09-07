from django.shortcuts import render

def home_view(request):
    """Landing page view"""
    context = {
        'title': 'Welcome to Software Tienda',
        'description': 'Your one-stop shop for software solutions',
    }
    return render(request, 'main/home.html', context)
