from django.db import models
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
# Create your models here.


class PayrollItems(models.Model):
    type = models.CharField(max_length=128, null=False, blank=False, verbose_name='Payroll items type')
    wage_items = models.CharField(max_length=128, null=False, blank=False, verbose_name='Wage items')
    notes = models.CharField(max_length=128, null=True, blank=True, verbose_name='Payroll notes')
    value = models.FloatField(null=False, blank=False, verbose_name='Value')

    def __str__(self):
        return 'type:{}   wage_items:{}   value:{}'.format(self.type, self.wage_items, self.value)


class Payroll(models.Model):
    serial_number = models.CharField(max_length=128, null=False, blank=False, verbose_name='Serial number')
    name = models.CharField(max_length=128, null=False, blank=False, verbose_name='Name')
    time = models.DateField(null=False, blank=False, verbose_name='time')
    CRN = models.CharField(max_length=128, null=False, blank=False, verbose_name='CRN')
    gender_choices = (('Male', 'Male'), ('Female', 'Female'))
    gender = models.CharField(max_length=128, null=False, blank=False, verbose_name='Gender', choices=gender_choices)
    department = models.CharField(max_length=128, null=False, blank=False, verbose_name='Department')
    Tax_ID = models.CharField(max_length=128, null=False, blank=False, verbose_name='Tax ID')
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name='Address')
    tel = models.CharField(max_length=64, null=True, blank=True, verbose_name='Tel')
    bank_of_account = models.CharField(max_length=128, null=True, blank=True, verbose_name='Bank of Account')
    account_number = models.CharField(max_length=128, null=True, blank=True, verbose_name='Account Number')
    payroll_items = models.ManyToManyField(to=PayrollItems, blank=False, verbose_name='Payroll item')
    salary_item_amount = models.CharField(max_length=128, null=False, blank=False, verbose_name='Salary item amount')
    currency = models.CharField(max_length=128, null=True, blank=True, verbose_name='Currency')
    total_wages = models.FloatField(null=True, blank=True, verbose_name='Total wages',
                                    help_text='The value of this field will be based on the payroll_ Automatic calculation of items field')

    def __str__(self):
        return '<serial_number:{} name:{}>'.format(self.serial_number, self.name)

