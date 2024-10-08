from django.contrib import admin
from .models import PayrollItems, Payroll
# Register your models here.

class PayrollItemsAdmin(admin.ModelAdmin):
    pass
admin.site.register(PayrollItems, PayrollItemsAdmin)

class PayrollAdmin(admin.ModelAdmin):
    def save_related(self, request, form, formsets, change):
        super(PayrollAdmin, self).save_related(request, form, formsets, change)
        total_wages = 0
        for i in form.instance.payroll_items.all():
            total_wages += i.value
        form.instance.total_wages = total_wages
        form.instance.save()
admin.site.register(Payroll, PayrollAdmin)