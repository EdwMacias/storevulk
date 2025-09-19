from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import CustomUserCreationForm, LoginForm, UserEditForm
from .models import User
from .decorators import admin_required

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Cuenta creada exitosamente! Por favor inicia sesión.')
        return response

def login_view(request):
    if request.user.is_authenticated:
        return redirect('main:dashboard')
    
    form = LoginForm()
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido, {user.username}!')
                next_url = request.GET.get('next', 'main:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('accounts:login')

# Admin-only views for user management
@method_decorator(admin_required, name='dispatch')
class AdminUserListView(ListView):
    model = User
    template_name = 'accounts/admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        return User.objects.all().order_by('-created_at')

@method_decorator(admin_required, name='dispatch')
class AdminUserCreateView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/admin/user_create.html'
    success_url = reverse_lazy('accounts:admin_user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Usuario {self.object.username} creado exitosamente.')
        return response

@method_decorator(admin_required, name='dispatch')
class AdminUserUpdateView(UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'accounts/admin/user_edit.html'
    success_url = reverse_lazy('accounts:admin_user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Usuario {self.object.username} actualizado exitosamente.')
        return response

@admin_required
def admin_user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.user == user:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('accounts:admin_user_list')

    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Usuario {username} eliminado exitosamente.')
        return redirect('accounts:admin_user_list')

    return render(request, 'accounts/admin/user_delete.html', {'user_obj': user})

@admin_required
def admin_dashboard(request):
    user_stats = {
        'total_users': User.objects.count(),
        'admin_users': User.objects.filter(role='admin').count(),
        'regular_users': User.objects.filter(role='user').count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'recent_users': User.objects.order_by('-created_at')[:5]
    }
    return render(request, 'accounts/admin/dashboard.html', {'stats': user_stats})
