from django.urls import path
from . import views

app_name = 'caja'

urlpatterns = [
    # Dashboard
    path('', views.caja_dashboard, name='dashboard'),

    # Cash Register Management
    path('abrir/', views.open_cash_register, name='open_register'),
    path('cerrar/<int:register_id>/', views.close_cash_register, name='close_register'),
    path('reporte/<int:report_id>/', views.closing_report_view, name='closing_report'),

    # Transactions
    path('transacciones/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transacciones/nueva/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('transacciones/nueva/<str:transaction_type>/', views.TransactionCreateView.as_view(), name='transaction_create_type'),
]