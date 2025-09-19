from django.contrib import admin
from django.utils.html import format_html
from .models import Bank, Entity, CashRegister, Transaction, CashRegisterReport

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity_type', 'code', 'is_active', 'created_at')
    list_filter = ('entity_type', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)

@admin.register(CashRegister)
class CashRegisterAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'current_balance', 'opened_by', 'opened_at')
    list_filter = ('status', 'opened_at', 'closed_at')
    search_fields = ('name', 'notes')
    readonly_fields = ('current_balance', 'created_at', 'updated_at')
    ordering = ('-opened_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('opened_by', 'closed_by')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('description', 'transaction_type', 'category', 'amount', 'payment_method', 'entity', 'commission', 'user', 'transaction_date')
    list_filter = ('transaction_type', 'category', 'payment_method', 'entity', 'bank', 'transaction_date', 'created_at')
    search_fields = ('description', 'reference_number', 'notes')
    readonly_fields = ('net_amount', 'created_at', 'updated_at')
    ordering = ('-transaction_date',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'bank', 'entity', 'cash_register')

    def net_amount(self, obj):
        return f"${obj.net_amount:,.2f}"
    net_amount.short_description = 'Monto Neto'

@admin.register(CashRegisterReport)
class CashRegisterReportAdmin(admin.ModelAdmin):
    list_display = ('cash_register', 'opening_balance', 'closing_balance', 'total_income', 'total_outcome', 'transaction_count', 'has_cash_discrepancy', 'created_at')
    list_filter = ('cash_register__status', 'created_at')
    search_fields = ('cash_register__name', 'notes')
    readonly_fields = ('expected_cash_balance', 'has_cash_discrepancy', 'created_at')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cash_register', 'cash_register__opened_by')

    def has_cash_discrepancy(self, obj):
        if obj.has_cash_discrepancy:
            return format_html('<span style="color: red;">Sí (${:.2f})</span>', abs(obj.cash_difference))
        return format_html('<span style="color: green;">No</span>')
    has_cash_discrepancy.short_description = 'Discrepancia'
