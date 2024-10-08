# Generated by Django 4.1.5 on 2023-09-25 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0016_invoice_sub_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default='Not Issued', max_digits=10),
        ),
    ]
