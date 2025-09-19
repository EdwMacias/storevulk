from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Admin-only user management URLs
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/create/', views.AdminUserCreateView.as_view(), name='admin_user_create'),
    path('admin/users/<int:pk>/edit/', views.AdminUserUpdateView.as_view(), name='admin_user_edit'),
    path('admin/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
]