# Generated by Django 4.1.5 on 2023-10-26 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0054_delete_supplier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='payment_terms',
            field=models.CharField(blank=True, choices=[('Net30', 'Net 30 Days'), ('Net60', 'Net 60 Days'), ('NetEOM', 'Net End of Month')], default='Net30', max_length=50, null=True, verbose_name='Payment Terms'),
        ),
    ]