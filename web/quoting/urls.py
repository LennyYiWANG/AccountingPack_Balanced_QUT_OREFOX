from django.urls import path
from . import views


app_name = 'quoting'

# All paths for url mapping to functions in quoting
urlpatterns = [
    path('', views.quoting_menu, name='quoting'),
    path('get_quotes/', views.get_quotes, name='get_quotes'),
    path('create_quote/', views.create_quote, name='create_quote'),
    path('view_quote/<int:quote_id>/', views.view_quote, name='view_quote'),
    path('get_quote_id/<int:quote_id>/', views.get_quote_id, name='get_quote_id'),
    path('get_quote_status/<int:quote_id>/', views.get_quote_status, name='get_quote_status'),
    path('edit_quote/', views.edit_quote, name='edit_quote'),
    path('get_quote_totals/<int:quote_id>/', views.get_quote_totals, name='get_quote_totals'),
    path('get_line_items/<int:quote_id>/', views.get_line_items, name='get_line_items'),
    path('get_line_item/<int:line_item_id>/', views.get_line_item, name='get_line_item'),
    path('add_line_item/<int:quote_id>/', views.add_line_item, name='add_line_item'),
    path('delete_line_items/', views.delete_line_items, name='delete_line_items'),
    path('edit_line_item/<int:line_item_id>/', views.edit_line_item, name='edit_line_item'),
    path('delete_quotes/', views.delete_quotes, name='delete_quotes'),
    path('get_quote_id/<int:quote_id>/', views.get_quote_id, name='get_quote_id'),
    path('get_quote_pdf/<int:quote_id>/', views.get_quote_pdf, name='get_quote_pdf'),
    path('send_quote_email/<int:quote_id>/', views.send_quote_email, name='send_quote_email'),
    path('quote_as_paid/<uuid:token>/', views.quote_as_paid, name='quote_as_paid'),
]

