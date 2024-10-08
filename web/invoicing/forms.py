from django import forms
from django.forms import DateInput
from .models import Invoice
from .models import LineItem
from .models import Client

# Client form for creating a new client in invoicing.html
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name','email', 'company_name', 'billing_address_street', 
                  'billing_address_state', 'billing_address_city', 'billing_address_postal_code', 'contact_phone', 
                  'aus_business_number','tax_file_number', 'payment_terms' ]

# Invoice form for creating a new invoice in invoicing.html
class InvoiceForm(forms.ModelForm):
    client = forms.ModelChoiceField(queryset=Client.objects.all())
    class Meta:
        model = Invoice
        fields = ['client', 'date', 'shipping', 'discount']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }

# Line item form for adding a new line item in invoice_viewer.html
class LineItemForm(forms.ModelForm):
    class Meta:
        model = LineItem
        fields = ['description', 'quantity', 'unit_price']
