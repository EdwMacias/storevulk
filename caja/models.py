from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()

class Bank(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre del Banco')
    code = models.CharField(max_length=10, unique=True, verbose_name='Código')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Banco'
        verbose_name_plural = 'Bancos'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

class Entity(models.Model):
    ENTITY_TYPES = [
        ('bank', 'Banco'),
        ('payment_platform', 'Plataforma de Pago'),
        ('cash', 'Efectivo'),
        ('other', 'Otro'),
    ]

    name = models.CharField(max_length=100, verbose_name='Nombre de la Entidad')
    entity_type = models.CharField(
        max_length=20,
        choices=ENTITY_TYPES,
        default='other',
        verbose_name='Tipo de Entidad'
    )
    code = models.CharField(max_length=20, unique=True, verbose_name='Código')
    description = models.TextField(blank=True, verbose_name='Descripción')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Entidad'
        verbose_name_plural = 'Entidades'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_entity_type_display()})"

class CashRegister(models.Model):
    STATUS_CHOICES = [
        ('open', 'Abierta'),
        ('closed', 'Cerrada'),
        ('suspended', 'Suspendida'),
    ]

    name = models.CharField(max_length=100, verbose_name='Nombre de Caja')
    opening_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Saldo Inicial'
    )
    current_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Saldo Actual'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='closed',
        verbose_name='Estado'
    )
    opened_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='opened_registers',
        null=True,
        blank=True,
        verbose_name='Abierta por'
    )
    closed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='closed_registers',
        null=True,
        blank=True,
        verbose_name='Cerrada por'
    )
    opened_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Apertura')
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Cierre')
    notes = models.TextField(blank=True, verbose_name='Notas')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Caja Registradora'
        verbose_name_plural = 'Cajas Registradoras'
        ordering = ['-opened_at']

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"

    def calculate_balance(self):
        """Calcula el balance basado en las transacciones"""
        income_total = self.transactions.filter(
            transaction_type='income'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

        outcome_total = self.transactions.filter(
            transaction_type='outcome'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

        return self.opening_balance + income_total - outcome_total

    def update_balance(self):
        """Actualiza el balance actual"""
        self.current_balance = self.calculate_balance()
        self.save(update_fields=['current_balance'])

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Ingreso'),
        ('outcome', 'Egreso'),
    ]

    PAYMENT_METHODS = [
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia'),
        ('card', 'Tarjeta'),
        ('check', 'Cheque'),
        ('digital_wallet', 'Billetera Digital'),
        ('other', 'Otro'),
    ]

    CATEGORY_CHOICES = [
        ('general_transaction', 'Transacción General'),
        ('papeleria_sale', 'Venta de Papelería'),
        ('bank_operation', 'Operación Bancaria'),
        ('commission_income', 'Ingreso por Comisiones'),
        ('expense_operational', 'Gasto Operacional'),
        ('expense_supplies', 'Gasto en Suministros'),
        ('cash_adjustment', 'Ajuste de Caja'),
        ('other_income', 'Otros Ingresos'),
        ('other_expense', 'Otros Gastos'),
    ]

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        verbose_name='Tipo de Transacción'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor'
    )
    description = models.CharField(max_length=255, verbose_name='Descripción')
    category = models.CharField(
        max_length=25,
        choices=CATEGORY_CHOICES,
        default='general_transaction',
        verbose_name='Categoría'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='cash',
        verbose_name='Método de Pago'
    )
    bank = models.ForeignKey(
        Bank,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Banco'
    )
    entity = models.ForeignKey(
        Entity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Entidad'
    )
    commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Comisión'
    )
    commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='% Comisión',
        help_text='Porcentaje de comisión aplicado'
    )
    reference_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Número de Referencia'
    )
    notes = models.TextField(blank=True, verbose_name='Notas')
    cash_register = models.ForeignKey(
        CashRegister,
        on_delete=models.CASCADE,
        related_name='transactions',
        null=True,
        blank=True,
        verbose_name='Caja Registradora'
    )

    # Tracking fields
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario que registra'
    )
    transaction_date = models.DateTimeField(verbose_name='Fecha de Transacción')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['-transaction_date', '-created_at']

    def __str__(self):
        type_symbol = '+' if self.transaction_type == 'income' else '-'
        return f"{type_symbol}${self.amount} - {self.description} ({self.transaction_date.strftime('%d/%m/%Y')})"

    @property
    def net_amount(self):
        """Retorna el monto neto después de comisiones"""
        if self.transaction_type == 'income':
            return self.amount - self.commission
        else:
            return self.amount + self.commission

    def save(self, *args, **kwargs):
        """Actualiza el balance de la caja al guardar"""
        super().save(*args, **kwargs)
        if self.cash_register:
            self.cash_register.update_balance()

class CashRegisterReport(models.Model):
    """Reporte detallado del cierre de caja"""
    cash_register = models.OneToOneField(
        CashRegister,
        on_delete=models.CASCADE,
        related_name='closing_report',
        verbose_name='Caja Registradora'
    )

    # Summary totals
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Saldo Inicial')
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Saldo Final')
    total_income = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Total Ingresos')
    total_outcome = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Total Egresos')
    total_commissions = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Total Comisiones')

    # Breakdown by category
    papeleria_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Ingresos Papelería')
    bank_operations_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Ingresos Operaciones Bancarias')
    commission_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Ingresos por Comisiones')
    general_transactions_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Ingresos Transacciones Generales')
    other_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Otros Ingresos')

    # Breakdown by payment method
    cash_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Total Efectivo')
    transfer_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Total Transferencias')
    card_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Total Tarjetas')
    other_payment_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Otros Métodos de Pago')

    # Cash reconciliation
    physical_cash_count = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Conteo Físico de Efectivo'
    )
    cash_difference = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Diferencia en Efectivo'
    )

    # Metadata
    transaction_count = models.IntegerField(default=0, verbose_name='Número de Transacciones')
    shift_duration_minutes = models.IntegerField(null=True, blank=True, verbose_name='Duración del Turno (minutos)')
    notes = models.TextField(blank=True, verbose_name='Notas del Cierre')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reporte de Cierre de Caja'
        verbose_name_plural = 'Reportes de Cierre de Caja'
        ordering = ['-created_at']

    def __str__(self):
        return f"Reporte - {self.cash_register.name} ({self.cash_register.closed_at.strftime('%d/%m/%Y')})"

    @property
    def expected_cash_balance(self):
        """Calcula el balance de efectivo esperado"""
        return self.opening_balance + self.cash_total

    @property
    def has_cash_discrepancy(self):
        """Verifica si hay discrepancia en el efectivo"""
        return self.physical_cash_count is not None and abs(self.cash_difference) > Decimal('0.01')
