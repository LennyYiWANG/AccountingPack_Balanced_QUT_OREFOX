# Generated by Django 4.1.5 on 2023-09-08 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0011_remove_inputinvoicing_invoicing_file_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesinvoicing',
            name='invoicing_file',
        ),
    ]