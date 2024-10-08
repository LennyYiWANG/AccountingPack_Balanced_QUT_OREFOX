# Generated by Django 4.1.5 on 2023-10-06 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0029_alter_invoice_discount_alter_invoice_shipping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='discount',
            field=models.DecimalField(blank=True, decimal_places=2, default='0.00', max_digits=5),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='tax',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Tax'),
        ),
    ]
