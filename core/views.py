from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import get_template
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from xhtml2pdf import pisa
from datetime import date, timedelta, datetime

from .models import Drug, Sale
from .forms import DrugForm, SaleForm
from django.db.models import Sum
from django.utils import timezone
from .models import Drug, Sale


User = get_user_model()

# ------------------------------
# Dashboard
# ------------------------------
@login_required
def dashboard(request):
    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    total_drugs = Drug.objects.aggregate(total=Sum('quantity'))['total'] or 0

    today_sales = Sale.objects.filter(date_sold=today).aggregate(total=Sum('total_amount'))['total'] or 0
    monthly_sales = Sale.objects.filter(date_sold__gte=start_of_month).aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'total_drugs': total_drugs,
        'today_sales': today_sales,
        'monthly_sales': monthly_sales,
    }
    return render(request, 'dashboard.html', context)


# ------------------------------
# Drug Views
# ------------------------------
@login_required
def drug_list(request):
    today = date.today()
    near_expiry = today + timedelta(days=30)

    drugs = Drug.objects.all().order_by('name')
    expiring_soon = drugs.filter(expiry_date__range=(today, near_expiry))
    expired = drugs.filter(expiry_date__lt=today)

    return render(request, 'drug_list.html', {
        'drugs': drugs,
        'expiring_soon': expiring_soon,
        'expired': expired,
    })

@login_required
def drug_add(request):
    if request.method == 'POST':
        form = DrugForm(request.POST)
        if form.is_valid():
            drug = form.save(commit=False)
            drug.created_by = request.user
            drug.updated_by = request.user
            drug.save()
            return redirect('drug_list')
    else:
        form = DrugForm()
    return render(request, 'drug_form.html', {'form': form})

@login_required
def drug_edit(request, pk):
    drug = get_object_or_404(Drug, pk=pk)
    if request.method == 'POST':
        form = DrugForm(request.POST, instance=drug)
        if form.is_valid():
            drug = form.save(commit=False)
            drug.updated_by = request.user
            drug.save()
            return redirect('drug_list')
    else:
        form = DrugForm(instance=drug)
    return render(request, 'drug_form.html', {'form': form})

@login_required
def drug_delete(request, pk):
    if not request.user.is_admin():
        return HttpResponseForbidden("Only admins can delete drugs.")
    drug = get_object_or_404(Drug, pk=pk)
    if request.method == 'POST':
        drug.delete()
        return redirect('drug_list')
    return render(request, 'drug_confirm_delete.html', {'drug': drug})

# ------------------------------
# Sale Views
# ------------------------------
@login_required
def sale_add(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.created_by = request.user
            sale.save()
            return redirect('sale_list')
    else:
        form = SaleForm()
    return render(request, 'sale_form.html', {'form': form})

@login_required
def sale_list(request):
    sales = Sale.objects.all().order_by('-date_sold')
    return render(request, 'sale_list.html', {'sales': sales})

# ------------------------------
# Sales Summary
# ------------------------------
@login_required
def sales_summary(request):
    start = request.GET.get('start')
    end = request.GET.get('end')

    sales = Sale.objects.all()
    if start and end:
        sales = sales.filter(date_sold__range=[start, end])

    total = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    return render(request, 'sales_summary.html', {
        'sales': sales,
        'total': total,
        'start_date': start,
        'end_date': end,
    })

# ------------------------------
# PDF Export
# ------------------------------
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation error <pre>' + html + '</pre>')
    return response

@login_required
def export_sales_pdf(request):
    today = datetime.today().date()
    month_start = today.replace(day=1)
    sales = Sale.objects.filter(date_sold__gte=month_start)

    context = {
        'sales': sales,
        'date_generated': today,
    }
    return render_to_pdf('sales_pdf.html', context)

# ------------------------------
# Profit Report
# ------------------------------
@login_required
def profit_report(request):
    start = request.GET.get('start')
    end = request.GET.get('end')

    sales = Sale.objects.all()
    if start and end:
        sales = sales.filter(date_sold__range=[start, end])

    total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or 0
    total_cost = sales.aggregate(
        total=Sum(ExpressionWrapper(
            F('drug__cost_price') * F('quantity_sold'),
            output_field=DecimalField()
        ))
    )['total'] or 0

    profit = total_sales - total_cost

    return render(request, 'profit_report.html', {
        'sales': sales,
        'total_sales': total_sales,
        'total_cost': total_cost,
        'profit': profit,
        'start_date': start,
        'end_date': end,
    })

# ------------------------------
# Create Staff Account (Admin only)
# ------------------------------
@login_required
def create_staff_account(request):
    if not request.user.is_admin():
        return HttpResponseForbidden("Only admins can create accounts.")

    class StaffCreationForm(UserCreationForm):
        class Meta:
            model = User
            fields = ['username', 'email', 'password1', 'password2']

        def save(self, commit=True):
            user = super().save(commit=False)
            user.role = 'staff'
            if commit:
                user.save()
            return user

    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = StaffCreationForm()

    return render(request, 'create_staff.html', {'form': form})

#expot profit pdf

@login_required
def export_profit_pdf(request):
    start = request.GET.get('start')
    end = request.GET.get('end')

    sales = Sale.objects.all()
    if start and end:
        sales = sales.filter(date_sold__range=[start, end])

    total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or 0
    total_cost = sales.aggregate(
        total=Sum(ExpressionWrapper(
            F('drug__cost_price') * F('quantity_sold'),
            output_field=DecimalField()
        ))
    )['total'] or 0

    profit = total_sales - total_cost

    context = {
        'sales': sales,
        'total_sales': total_sales,
        'total_cost': total_cost,
        'profit': profit,
        'start_date': start,
        'end_date': end,
    }

    return render_to_pdf('profit_pdf.html', context)

@login_required
def dashboard(request):
    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    total_drugs = Drug.objects.aggregate(total=Sum('quantity'))['total'] or 0
    today_sales = Sale.objects.filter(date_sold=today).aggregate(total=Sum('total_amount'))['total'] or 0
    monthly_sales = Sale.objects.filter(date_sold__gte=start_of_month).aggregate(total=Sum('total_amount'))['total'] or 0

    # New: get debtor sales (where not fully paid)
    debtors = Sale.objects.filter(total_amount__gt=F('amount_paid')).order_by('-date_sold')

    for sale in debtors:
        sale.debt_amount = sale.total_amount - sale.amount_paid

    context = {
        'total_drugs': total_drugs,
        'today_sales': today_sales,
        'monthly_sales': monthly_sales,
        'debtors': debtors,
    }
    return render(request, 'dashboard.html', context)

  # debtors

@login_required
def debtor_list(request):
    debtors = Debtor.objects.order_by('-date_sold')
    return render(request, 'debtor_list.html', {'debtors': debtors})


@login_required
def debtor_add(request):
    if request.method == 'POST':
        form = DebtorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('debtor_list')
    else:
        form = DebtorForm()
    return render(request, 'debtor_form.html', {'form': form})

from .forms import DebtorForm

@login_required
def debtor_add(request):
    if request.method == 'POST':
        form = DebtorForm(request.POST)
        if form.is_valid():
            debtor = form.save(commit=False)
            debtor.created_by = request.user
            debtor.save()
            return redirect('dashboard')  # Or 'debtor_list' if you want to show all
    else:
        form = DebtorForm()
    return render(request, 'debtor_form.html', {'form': form})

# views.py

from .models import Acknowledgement, Investor

def about_view(request):
    acknowledgements = Acknowledgement.objects.all()
    investors = Investor.objects.all()
    return render(request, 'about.html', {
        'acknowledgements': acknowledgements,
        'investors': investors,
    })

from django.shortcuts import render, redirect
from .forms import InvestorForm, AcknowledgementForm

def add_investor(request):
    if request.method == 'POST':
        form = InvestorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # or wherever you want
    else:
        form = InvestorForm()
    return render(request, 'add_investor.html', {'form': form})

def add_acknowledgement(request):
    if request.method == 'POST':
        form = AcknowledgementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = AcknowledgementForm()
    return render(request, 'add_acknowledgement.html', {'form': form})
