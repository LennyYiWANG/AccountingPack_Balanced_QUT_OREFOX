import uuid
from django.db import models
from invoicing.models import Client
from django.db.models import Sum
from decimal import Decimal

# Create your models here.

# Quote model with the Client model as a foregin key so that clients can be associated with a particular quote
class Quote(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('UNCONFIRMED', 'Unconfirmed'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField()
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True,  default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='UNCONFIRMED',
    )
    # Code to calculate totals for quotes. Sums up all line items, applying discounts and shipping costs
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

# Line item model to store all the items created for a particular quote
class LineItem(models.Model): # make the same in quoting
    quote = models.ForeignKey(Quote, related_name='line_items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.PositiveBigIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(verbose_name='Tax', max_digits=10, decimal_places=2)
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        self.tax = self.line_total * Decimal('0.10')
        super(LineItem, self).save(*args, **kwargs)
        self.quote.calculate_total()

# Token for the email recipient so only their actions are permitted.
class QuoteActionToken(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_used = models.BooleanField(default=False)
