from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Drug, Sale, Debtor
from django import forms
from .models import Investor, Acknowledgement

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

class DrugForm(forms.ModelForm):
    class Meta:
        model = Drug
        fields = [
            'name', 'batch_number', 'expiry_date',
            'quantity', 'cost_price', 'selling_price', 'supplier'
        ]

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['drug', 'quantity_sold', 'sale_price']

class DebtorForm(forms.ModelForm):
    class Meta:
        model = Debtor
        fields = ['drug', 'quantity_sold', 'total_amount', 'customer_name', 'date_sold', 'notes']
class InvestorForm(forms.ModelForm):
    class Meta:
        model = Investor
        fields = ['name', 'image']

class AcknowledgementForm(forms.ModelForm):
    class Meta:
        model = Acknowledgement
        fields = ['description', 'image']