# Generated by Django 4.1.5 on 2023-09-08 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0009_inputinvoicing_invoicing_due_date_lineitem_tax_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesinvoicing',
            name='total_price',
            field=models.FloatField(blank=True, null=True, verbose_name='Total Price'),
        ),
    ]