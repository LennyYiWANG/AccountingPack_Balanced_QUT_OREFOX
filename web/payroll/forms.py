from django import forms
from . import models
from django.forms import widgets
from django.core.exceptions import ValidationError
import re


class PayrollItemsForms(forms.ModelForm):
    class Meta:
        model = models.PayrollItems
        fields = "__all__"
        exclude = None

        # widgets = {
        #     "sequences": widgets.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter...'}),
        #     "sequences_file": widgets.FileInput(attrs={'class': 'form-control', 'placeholder': 'Upload...'}),
        # }


class PayrollForms(forms.ModelForm):
    class Meta:
        model = models.Payroll
        fields = "__all__"
        exclude = None




