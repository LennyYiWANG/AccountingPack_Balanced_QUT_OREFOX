import uuid
from django.db import models
from django.db.models import Sum
from decimal import Decimal

# Create your models here.

# Client model that contains all payment information and address information for all the clients
class Client(models.Model):
    PAYMENT_TERMS_CHOICES = [
        ('Net30', 'Net 30 Days'),
        ('Net60', 'Net 60 Days'),
        ('NetEOM', 'Net End of Month'),
    ]
    BILLING_ADDRESS_STATE_OPTIONS =[
        ('QLD', 'QLD'),
        ('NSW', 'NSW'),
        ('VIC', 'VIC'),
        ('WA', 'WA'),
        ('SA', 'SA'),
        ('NT', 'NT'),
        ('TAS', 'TAS'),
        ('ACT', 'ACT'),
    ]
    name = models.CharField(max_length=255)
    email = models.EmailField()
    company_name = models.TextField(verbose_name='Company Name', null=False, default='Unknown')
    billing_address_street = models.CharField(max_length=255, verbose_name='Billing Street', null=False, default='Unknown')
    billing_address_city = models.CharField(max_length=50, verbose_name='Billing City', null=False, default='Unknown')
    billing_address_state = models.CharField(
        max_length=3, 
        verbose_name='Address State', 
        choices=BILLING_ADDRESS_STATE_OPTIONS, 
        default='QLD'
    )
    billing_address_postal_code = models.CharField(max_length=20, verbose_name='Billing Postal Code', null=False, default='Unknown')
    contact_phone = models.CharField(max_length=20, verbose_name='Contact Phone', null=False, default='Unknown')
    tax_file_number = models.CharField(max_length=20, verbose_name='Tax File Number', blank=True, null=True)
    aus_business_number = models.CharField(max_length=20, verbose_name='ABN', blank=True, null=True)
    payment_terms = models.CharField(
        max_length=50, 
        verbose_name='Payment Terms', 
        choices=PAYMENT_TERMS_CHOICES, 
        default='Net30',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

# Invoice model with the Client model as a foregin key so that clients can be associated with a particular invoice
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
        ('UNPAID', 'Unpaid'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField()
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True,  default=0)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='UNPAID',
    )
  # Code to calculate totals for invoices. Sums up all line items, applying discounts and shipping costs
    # Recalculates each time a line item is added
    def calculate_total(self):
        line_items = self.line_items.all()

        # Sum of line_total for all line items
        agg_line_total = line_items.aggregate(Sum('line_total'))
        self.sub_total = agg_line_total['line_total__sum'] if agg_line_total['line_total__sum'] else Decimal('0.00')

        agg_tax = line_items.aggregate(Sum('tax'))
        self.tax = agg_tax['tax__sum'] if agg_tax['tax__sum'] else Decimal('0.00')

        self.total_amount = Decimal('0.00')
        discount_amount = (self.discount / Decimal('100.0')) * self.sub_total

        self.total_amount += self.sub_total
        self.total_amount -= discount_amount

        self.total_amount += Decimal(str(self.tax))

        if self.shipping is not None:
            self.total_amount += self.shipping

        self.save()

# Line item model to store all the items created for a particular invoice
class LineItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='line_items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.PositiveBigIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(verbose_name='Tax', max_digits=10, decimal_places=2)
    # Calculates the total price of each item by quantity and unit price
    # Calculates tax for each line item
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        self.tax = self.line_total * Decimal('0.10')
        super(LineItem, self).save(*args, **kwargs)
        self.invoice.calculate_total()

# Token for the email recipient so only their actions are permitted.
class InvoiceActionToken(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_used = models.BooleanField(default=False)

