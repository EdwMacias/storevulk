from django import forms
from django.utils import timezone
from .models import Transaction, CashRegister, Bank, Entity

class CashRegisterForm(forms.ModelForm):
    class Meta:
        model = CashRegister
        fields = ['name', 'opening_balance', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Caja Principal'
            }),
            'opening_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas opcionales sobre la apertura de caja'
            }),
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'transaction_type', 'amount', 'description', 'category', 'payment_method',
            'bank', 'entity', 'commission', 'commission_percentage',
            'reference_number', 'notes'
        ]
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'transaction_type'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00',
                'id': 'amount'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la transacción'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'category'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select',
                'id': 'payment_method'
            }),
            'bank': forms.Select(attrs={
                'class': 'form-select',
                'id': 'bank'
            }),
            'entity': forms.Select(attrs={
                'class': 'form-select',
                'id': 'entity'
            }),
            'commission': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
                'id': 'commission'
            }),
            'commission_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '0.00',
                'id': 'commission_percentage'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de referencia o comprobante'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter active entities and banks
        self.fields['bank'].queryset = Bank.objects.filter(is_active=True)
        self.fields['entity'].queryset = Entity.objects.filter(is_active=True)

        # Make bank and entity optional
        self.fields['bank'].required = False
        self.fields['entity'].required = False

        # Set initial transaction type if provided in URL
        if 'initial' in kwargs and 'transaction_type' in kwargs['initial']:
            self.fields['transaction_type'].initial = kwargs['initial']['transaction_type']

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        bank = cleaned_data.get('bank')
        entity = cleaned_data.get('entity')
        amount = cleaned_data.get('amount')
        commission = cleaned_data.get('commission')
        commission_percentage = cleaned_data.get('commission_percentage')

        # Validate bank requirement for certain payment methods
        if payment_method in ['transfer', 'card'] and not bank:
            raise forms.ValidationError(
                'Debes seleccionar un banco para transferencias y pagos con tarjeta.'
            )

        # Calculate commission if percentage is provided
        if commission_percentage and amount:
            calculated_commission = amount * (commission_percentage / 100)
            if commission and abs(commission - calculated_commission) > 0.01:
                cleaned_data['commission'] = calculated_commission

        return cleaned_data

class TransactionFilterForm(forms.Form):
    TRANSACTION_TYPE_CHOICES = [
        ('', 'Todos los tipos'),
        ('income', 'Ingresos'),
        ('outcome', 'Egresos'),
    ]

    transaction_type = forms.ChoiceField(
        choices=TRANSACTION_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default date range to current month
        today = timezone.now().date()
        first_day = today.replace(day=1)
        self.fields['date_from'].initial = first_day
        self.fields['date_to'].initial = today

class CashReconciliationForm(forms.Form):
    physical_cash_count = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        label='Conteo Físico de Efectivo',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        }),
        help_text='Ingresa la cantidad de efectivo contada físicamente en la caja'
    )

    notes = forms.CharField(
        required=False,
        label='Notas del Cierre',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observaciones sobre el cierre de caja (opcional)'
        })
    )