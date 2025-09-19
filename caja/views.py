from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
from .models import CashRegister, Transaction, Bank, Entity, CashRegisterReport
from .forms import TransactionForm, CashRegisterForm, CashReconciliationForm

@login_required
def caja_dashboard(request):
    # Get user's current cash register
    current_register = CashRegister.objects.filter(
        opened_by=request.user,
        status='open'
    ).first()

    # Recent transactions
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('bank', 'entity', 'cash_register')[:10]

    # Daily summary
    today = timezone.now().date()
    daily_income = Transaction.objects.filter(
        user=request.user,
        transaction_type='income',
        transaction_date__date=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    daily_outcome = Transaction.objects.filter(
        user=request.user,
        transaction_type='outcome',
        transaction_date__date=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    context = {
        'current_register': current_register,
        'recent_transactions': recent_transactions,
        'daily_income': daily_income,
        'daily_outcome': daily_outcome,
        'daily_balance': daily_income - daily_outcome,
    }

    return render(request, 'caja/dashboard.html', context)

@login_required
def open_cash_register(request):
    # Check if user already has an open register
    existing_register = CashRegister.objects.filter(
        opened_by=request.user,
        status='open'
    ).first()

    if existing_register:
        messages.warning(request, f'Ya tienes una caja abierta: {existing_register.name}')
        return redirect('caja:dashboard')

    if request.method == 'POST':
        form = CashRegisterForm(request.POST)
        if form.is_valid():
            register = form.save(commit=False)
            register.opened_by = request.user
            register.status = 'open'
            register.opened_at = timezone.now()
            register.current_balance = register.opening_balance
            register.save()

            messages.success(request, f'Caja {register.name} abierta exitosamente con ${register.opening_balance}')
            return redirect('caja:dashboard')
    else:
        form = CashRegisterForm()

    return render(request, 'caja/open_register.html', {'form': form})

@login_required
def close_cash_register(request, register_id):
    register = get_object_or_404(
        CashRegister,
        id=register_id,
        opened_by=request.user,
        status='open'
    )

    if request.method == 'POST':
        form = CashReconciliationForm(request.POST)
        if form.is_valid():
            # Generate comprehensive closing report
            report = generate_closing_report(register)

            # Add reconciliation data
            report.physical_cash_count = form.cleaned_data['physical_cash_count']
            report.cash_difference = report.physical_cash_count - report.expected_cash_balance
            report.notes = form.cleaned_data['notes']
            report.save()

            # Close the register
            register.status = 'closed'
            register.closed_by = request.user
            register.closed_at = timezone.now()
            register.save()

            messages.success(request, f'Caja {register.name} cerrada exitosamente. Balance final: ${register.current_balance}')
            return redirect('caja:closing_report', report_id=report.id)
    else:
        form = CashReconciliationForm()

    # Generate summary for preview
    summary = calculate_shift_summary(register)

    context = {
        'register': register,
        'form': form,
        'summary': summary,
    }

    return render(request, 'caja/close_register.html', context)

def generate_closing_report(register):
    """Generate comprehensive closing report"""
    from django.utils import timezone

    transactions = register.transactions.all()

    # Calculate shift duration
    shift_duration = None
    if register.opened_at:
        duration_delta = timezone.now() - register.opened_at
        shift_duration = int(duration_delta.total_seconds() / 60)  # minutes

    # Basic totals
    income_transactions = transactions.filter(transaction_type='income')
    outcome_transactions = transactions.filter(transaction_type='outcome')

    total_income = income_transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_outcome = outcome_transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_commissions = transactions.aggregate(total=Sum('commission'))['total'] or Decimal('0.00')

    # Category breakdown (income only)
    papeleria_income = income_transactions.filter(
        category='papeleria_sale'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    bank_operations_income = income_transactions.filter(
        category='bank_operation'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    commission_income = income_transactions.filter(
        category='commission_income'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    general_transactions_income = income_transactions.filter(
        category='general_transaction'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    other_income = income_transactions.filter(
        category__in=['other_income', 'cash_adjustment']
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Payment method breakdown (all transactions)
    cash_total = transactions.filter(
        payment_method='cash', transaction_type='income'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Subtract cash outcomes
    cash_outcomes = transactions.filter(
        payment_method='cash', transaction_type='outcome'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    cash_total -= cash_outcomes

    transfer_total = transactions.filter(
        payment_method='transfer'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    card_total = transactions.filter(
        payment_method='card'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    other_payment_total = transactions.filter(
        payment_method__in=['check', 'digital_wallet', 'other']
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Create the report
    report = CashRegisterReport.objects.create(
        cash_register=register,
        opening_balance=register.opening_balance,
        closing_balance=register.current_balance,
        total_income=total_income,
        total_outcome=total_outcome,
        total_commissions=total_commissions,
        papeleria_income=papeleria_income,
        bank_operations_income=bank_operations_income,
        commission_income=commission_income,
        general_transactions_income=general_transactions_income,
        other_income=other_income,
        cash_total=cash_total,
        transfer_total=transfer_total,
        card_total=card_total,
        other_payment_total=other_payment_total,
        transaction_count=transactions.count(),
        shift_duration_minutes=shift_duration
    )

    return report

def calculate_shift_summary(register):
    """Calculate detailed shift summary for preview"""
    transactions = register.transactions.all()

    # Basic totals
    income_transactions = transactions.filter(transaction_type='income')
    outcome_transactions = transactions.filter(transaction_type='outcome')

    total_income = income_transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_outcome = outcome_transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Category breakdown
    category_breakdown = {}
    for choice_value, choice_label in Transaction.CATEGORY_CHOICES:
        amount = income_transactions.filter(category=choice_value).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        if amount > 0:
            category_breakdown[choice_label] = amount

    # Payment method breakdown
    payment_breakdown = {}
    for choice_value, choice_label in Transaction.PAYMENT_METHODS:
        income_amount = income_transactions.filter(payment_method=choice_value).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        outcome_amount = outcome_transactions.filter(payment_method=choice_value).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        net_amount = income_amount - outcome_amount
        if net_amount != 0:
            payment_breakdown[choice_label] = {
                'income': income_amount,
                'outcome': outcome_amount,
                'net': net_amount
            }

    # Expected cash balance
    cash_income = income_transactions.filter(payment_method='cash').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    cash_outcome = outcome_transactions.filter(payment_method='cash').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    expected_cash = register.opening_balance + cash_income - cash_outcome

    return {
        'total_income': total_income,
        'total_outcome': total_outcome,
        'net_total': total_income - total_outcome,
        'category_breakdown': category_breakdown,
        'payment_breakdown': payment_breakdown,
        'expected_cash': expected_cash,
        'transaction_count': transactions.count(),
        'final_balance': register.current_balance,
    }

@login_required
def closing_report_view(request, report_id):
    """View the detailed closing report"""
    report = get_object_or_404(
        CashRegisterReport,
        id=report_id,
        cash_register__opened_by=request.user
    )

    context = {
        'report': report,
        'register': report.cash_register,
    }

    return render(request, 'caja/closing_report.html', context)

@method_decorator(login_required, name='dispatch')
class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'caja/transaction_create.html'
    success_url = reverse_lazy('caja:dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.user = self.request.user
        transaction.transaction_date = timezone.now()

        # Get user's current register
        current_register = CashRegister.objects.filter(
            opened_by=self.request.user,
            status='open'
        ).first()

        if current_register:
            transaction.cash_register = current_register

        transaction.save()

        type_text = 'Ingreso' if transaction.transaction_type == 'income' else 'Egreso'
        messages.success(
            self.request,
            f'{type_text} de ${transaction.amount} registrado exitosamente'
        )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transaction_type'] = self.kwargs.get('transaction_type', 'income')
        return context

@method_decorator(login_required, name='dispatch')
class TransactionListView(ListView):
    model = Transaction
    template_name = 'caja/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        queryset = Transaction.objects.filter(
            user=self.request.user
        ).select_related('bank', 'entity', 'cash_register')

        # Filter by type
        transaction_type = self.request.GET.get('type')
        if transaction_type in ['income', 'outcome']:
            queryset = queryset.filter(transaction_type=transaction_type)

        # Filter by date range
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if date_from:
            queryset = queryset.filter(transaction_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(transaction_date__date__lte=date_to)

        return queryset.order_by('-transaction_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate totals
        queryset = self.get_queryset()
        context['total_income'] = queryset.filter(
            transaction_type='income'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        context['total_outcome'] = queryset.filter(
            transaction_type='outcome'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        context['net_total'] = context['total_income'] - context['total_outcome']

        return context
