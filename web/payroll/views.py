import datetime

from django.shortcuts import render, HttpResponse, redirect, reverse
from django.contrib.auth.decorators import login_required
from .models import PayrollItems, Payroll
from .forms import PayrollForms, PayrollItemsForms
# Create your views here.
@login_required
def index(request):
    datas = Payroll.objects.all()
    print(datas)
    return render(request, 'index.html', locals())


@login_required
def AddPayrollItem(request):
    if request.method == 'GET':
        payroll_items = PayrollItems.objects.all()
        #'M, d. Y'
        now = datetime.datetime.now()
        now_time = now

        return render(request, 'adding_a_payroll.html', locals())
    else:
        print(request.POST)
        post = request.POST.copy()
        payroll_items = post.getlist('payroll_items', [])
        total_wages = 0
        for i in payroll_items:
            total_wages += PayrollItems.objects.get(id=i).value

        post.setdefault('total_wages', total_wages)
        form = PayrollForms(data=post)
        if form.is_valid():
            form.save()
            return redirect(reverse('payroll:index'))
        else:
            payroll_items = PayrollItems.objects.all()
            # 'M, d. Y'
            now = datetime.datetime.now()
            now_time = '{}, {}. {}'.format(now.month, now.day, now.year)
            now_time = '{}-{}-{}'.format(now.year, now.month, now.day)
            return render(request, 'adding_a_payroll.html', locals())


@login_required
def EditPayrollItem(request, id):
    if request.method == 'GET':
        payroll_items = PayrollItems.objects.all()

        data = Payroll.objects.get(id=id)
        selected_payroll_items = [i.id for i in data.payroll_items.all()]
        form = PayrollForms(instance=data)
        return render(request, 'adding_a_payroll.html', locals())
    else:
        post = request.POST.copy()
        payroll_items = PayrollItems.objects.all()
        payroll_items_tmp = post.getlist('payroll_items', [])
        total_wages = 0
        for i in payroll_items_tmp:
            total_wages += PayrollItems.objects.get(id=i).value

        post.setdefault('total_wages', total_wages)
        data = Payroll.objects.get(id=id)
        selected_payroll_items = [i.id for i in data.payroll_items.all()]
        form = PayrollForms(instance=data, data=post)
        if form.is_valid():
            form.save()
            return redirect(reverse('payroll:index'))
        else:
            return render(request, 'adding_a_payroll.html', locals())



@login_required
def DelPayrollItem(request, id):

    data = Payroll.objects.get(id=id)
    data.delete()


    return redirect(reverse('payroll:index'))