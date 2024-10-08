from django.urls import path, re_path
from . import views

app_name = 'payroll'

urlpatterns = [
    path('AddPayrollItem/', views.AddPayrollItem, name='AddPayrollItem'),
    path('EditPayrollItem/<int:id>/', views.EditPayrollItem, name='EditPayrollItem'),
    path('DelPayrollItem/<int:id>/', views.DelPayrollItem, name='DelPayrollItem'),
    path('', views.index, name='index'),

]