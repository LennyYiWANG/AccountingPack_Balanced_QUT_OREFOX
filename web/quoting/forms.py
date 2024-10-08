from django import forms
from django.forms import DateInput
from .models import Quote
from .models import LineItem
from invoicing.models import Client

# Client form for creating a new client in quoting.html
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name','email', 'company_name', 'billing_address_street', 
                  'billing_address_state', 'billing_address_city', 'billing_address_postal_code', 'contact_phone', 
                  'aus_business_number','tax_file_number', 'payment_terms' ]

# Quote form for creating a new Quote in quoting.html
class QuoteForm(forms.ModelForm):
    client = forms.ModelChoiceField(queryset=Client.objects.all())
    class Meta:
        model = Quote
        fields = ['client', 'date', 'shipping', 'discount']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }

# Line item form for adding a new line item in quote_viewer.html
class LineItemForm(forms.ModelForm):
    class Meta:
        model = LineItem
        fields = ['description', 'quantity', 'unit_price']
