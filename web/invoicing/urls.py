from django.urls import path
from . import views

app_name = 'invoicing'

# All paths for url mapping to functions in invoicing
urlpatterns = [
    path('', views.invoicing_menu, name='invoicing'),
    path('get_invoices/', views.get_invoices, name='get_invoices'),
    path('create_invoice/', views.create_invoice, name='create_invoice'),
    path('get_clients/', views.get_clients, name='get_clients'),
    path('add_client/', views.add_client, name='add_client'),
    path('get_payment_terms/', views.get_payment_terms, name='get_payment_terms'),
    path('get_states/', views.get_states, name='get_states'),
    path('add_line_item/<int:invoice_id>/', views.add_line_item, name='add_line_item'),
    path('delete_line_items/', views.delete_line_items, name='delete_line_items'),
    path('get_line_item/<int:line_item_id>/', views.get_line_item, name='get_line_item'),
    path('edit_line_item/<int:line_item_id>/', views.edit_line_item, name='edit_line_item'),
    path('view_invoice/<int:invoice_id>/', views.view_invoice, name='view_invoice'),
    path('get_invoice_status/<int:invoice_id>/', views.get_invoice_status, name='get_invoice_status'),
    path('get_invoice_id/<int:invoice_id>/', views.get_invoice_id, name='get_invoice_id'),
    path('edit_invoice/', views.edit_invoice, name='edit_invoice'),
    path('get_line_items/<int:invoice_id>/', views.get_line_items, name='get_line_items'),
    path('get_invoice_totals/<int:invoice_id>/', views.get_invoice_totals, name='get_invoice_totals'),
    path('delete_invoices/', views.delete_invoices, name='delete_invoices'),
    path('get_invoice_pdf/<int:invoice_id>/', views.get_invoice_pdf, name='get_invoice_pdf'),
    path('send_invoice_email/<int:invoice_id>/', views.send_invoice_email, name='send_invoice_email'),
    path('invoice_as_paid/<uuid:token>/', views.invoice_as_paid, name='invoice_as_paid'),
]
    
