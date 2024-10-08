from django.forms import ValidationError
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from urllib.parse import urljoin
from django.core.mail import EmailMultiAlternatives
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404, render
from .models import Invoice, Client, LineItem, InvoiceActionToken
from .forms import InvoiceForm
import json
from .forms import LineItemForm
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from io import BytesIO
from .models import Invoice, LineItem
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer



# Create your views here.

# Renders the home page for invoicing
@login_required
def invoicing_menu(request):
    return render(request, 'invoicing.html')

# Retrieve the specific invoice from the database using the invoice id and view the invoice
@login_required
def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    context = {
        'invoice': invoice,
    }
    return render(request, 'invoicing_viewer.html', context)

# Retrieves all invoices from the database along with their fields. Each field is approprattely formatted
@login_required
def get_invoices(request):
    invoices = Invoice.objects.select_related('client').values('id', 'client__name','date', 'sub_total', 'shipping', 'discount', 'tax', 'total_amount', 'status')
    invoice_list = list(invoices)
    for invoice in  invoice_list:
        invoice['client'] = invoice.pop('client__name')
        invoice['date'] = invoice['date'].strftime('%d/%m/%Y')
        if invoice['discount'] != None:
            invoice['discount'] = "{:.2f}%".format(invoice['discount'])
        invoice['sub_total'] = "${:.2f}".format(invoice['sub_total'])
        if invoice['shipping'] != None:
            invoice['shipping'] = "${:.2f}".format(invoice['shipping'])
        invoice['tax'] = "${:.2f}".format(invoice['tax'])
        invoice['total_amount'] = "${:.2f}".format(invoice['total_amount'])
    return JsonResponse({'data': invoice_list})

# Retrieves only the status of the invoice so that it can be determined what table it goes into in invoicing.html
def get_invoice_status(request, invoice_id):
    try:

        invoice = Invoice.objects.get(pk=invoice_id)
        invoice_data = {
            'status': invoice.status,
        }
        
        return JsonResponse(invoice_data)
    
    except Invoice.DoesNotExist:
        return JsonResponse({'error': 'Invoice not found'}, status=404)

# Creates the invoice and posts the data to the data base. Initiall only with four fields, as adding line items will populate the remaining fields.
@login_required 
def create_invoice(request):
    print(request.POST)
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            if invoice.shipping is None:
                invoice.shipping = Decimal('0.00')
            if invoice.discount is None:
                invoice.discount = Decimal('0.00')
            invoice.save()
            return JsonResponse({
                'success': True,
                'invoice': {
                    'client': str(invoice.client),
                    'date': str(invoice.date),
                    'shipping': str(invoice.shipping),
                    'discount': str(invoice.discount),
                }
            })
        else:
            print(form.errors)
            return JsonResponse({'success': False, 'errors': form.errors})

# Retrieves the invoice id and it's details for when a checkbox is checked and the edit button is clicked
@login_required
def get_invoice_id(request, invoice_id):
    try:
        invoice = Invoice.objects.get(pk=invoice_id)
        data = {
            'id': invoice.id,
            'client': invoice.client.id,
            'date': invoice.date,
            'shipping': invoice.shipping,
            'discount': invoice.discount
        }
        return JsonResponse({'status': 'success', 'data': data})
    except Invoice.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invoice not found'})

# Posts the updated data to the database based on which invoice was being edited
@login_required
def edit_invoice(request):
    if request.method == 'POST':
        invoice_id = request.POST.get('id')
        client_id = request.POST.get('client')
        
        try:
            invoice = Invoice.objects.get(pk=invoice_id)
            client = get_object_or_404(Client, pk=client_id)
            
            invoice.client = client

            date = request.POST.get('date')
            shipping = request.POST.get('shipping', '0.0')
            discount = request.POST.get('discount', '0.0')

            if shipping == "":
                shipping = '0.0'
            if discount == "":
                discount = '0.0'

            invoice.date = date
            invoice.shipping = Decimal(shipping)
            invoice.discount = Decimal(discount)
            
            invoice.save()

            return JsonResponse({'status': 'success', 'message': 'Invoice updated successfully'})
        except Invoice.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invoice not found'})
        except ValidationError:
            return JsonResponse({'status': 'error', 'message': 'Validation Error'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

# Deletes the invoices from the database based on what invoices where checked. If multiple were checked, a list of id's is populated.
@login_required
def delete_invoices(request):
    data = json.loads(request.body)
    invoice_ids = data.get('invoice_ids', [])
    if request.method == "POST":
        if invoice_ids:
            if len(invoice_ids) == 1:
                invoice = get_object_or_404(Invoice, id=invoice_ids[0])
                invoice.delete()
            else:
                Invoice.objects.filter(id__in=invoice_ids).delete()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'no ids'})
    else:
        return HttpResponse(status=405)

# Deletes the line items based on what line item checkboxes were checked. If multiple were checked, a list if id's is populated.  
@login_required
def delete_line_items(request):
    if request.method == 'POST':
        invoice_id = request.POST.get('invoice_id')  # replace with actual invoice_id field
        ids_to_delete = request.POST.getlist('line_item_ids[]')
        line_items = LineItem.objects.filter(id__in=ids_to_delete, invoice_id=invoice_id)

        print("IDs to Delete:", ids_to_delete)
        print("Line Items to Delete:", line_items.query)

        deleted_count, _ = line_items.delete()

        if deleted_count > 0:
            invoice = Invoice.objects.get(pk=invoice_id)
            invoice.calculate_total()
            return JsonResponse({'status': 'success', 'message': 'Line items deleted successfully'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

# Retrives the line item based on id. When edit button is clicked in invoice_viewer, the details to be edited are retrieved from the database.
@login_required
def get_line_item(request, line_item_id):
    line_item = get_object_or_404(LineItem, pk=line_item_id)
    line_item_dict = {
        'description': line_item.description,
        'unit_price': str(line_item.unit_price),
        'quantity': line_item.quantity,
    }
    return JsonResponse(line_item_dict)

# Posts the updated line item data in the database based on the line item id
@login_required
def edit_line_item(request, line_item_id):
    line_item = get_object_or_404(LineItem, pk=line_item_id)

    if request.method == 'POST':
        form = LineItemForm(request.POST, instance=line_item)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True}, status=200)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

# Posts the new line item to the database with the invoice id it's associated with
@login_required 
def add_line_item(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    invoice.calculate_total()
    if request.method == 'POST':
        form = LineItemForm(request.POST)
        if form.is_valid(): 
            line_item = form.save(commit=False)
            line_item.invoice = invoice
            line_item.save()
            return JsonResponse({'success': True}, status=201)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)        

# Retrieves all the line items from the database associated with a particular invoice id so that the invoice template is populated
@login_required
def get_line_items(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    line_items = serialize('json', LineItem.objects.filter(invoice=invoice))
    return JsonResponse({'line_items': line_items})

# Responsible for recalculating the totals each time a line item is added and retireves them from the database
def get_invoice_totals(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    invoice.calculate_total()

    sub_total = str(invoice.sub_total)
    tax = str(invoice.tax)
    total_amount = str(invoice.total_amount)
    shipping = str(invoice.shipping if invoice.shipping else Decimal('0.00'))
    discount = str(invoice.discount if invoice.discount else Decimal('0.00'))

    return JsonResponse({
        'sub_total': sub_total,
        'tax': tax,
        'total_amount': total_amount,
        'shipping': shipping,
        'discount': discount,
    })

# Retrieves all the clients to populate the selection list in invoicing.html and quoting.html       
@login_required
def get_clients(request):
    clients = Client.objects.all().values('id', 'name')
    client_list = list(clients)
    return JsonResponse({'data': client_list})

# Posts the new client data to the data base for invoicing and quoting
def add_client(request):
    if request.method == "POST":
        name = request.POST.get('name', None)
        email = request.POST.get('email', None)
        company_name = request.POST.get('company_name', None)

        if name and email:
            new_client = Client.objects.create(name=name, email=email, company_name=company_name)
            new_client.save()
            return JsonResponse({'client_id': new_client.id, 'client_name': new_client.name}, status=200)
        else:
            return JsonResponse({'error': 'Invalid data'}, status=400)

# Retrieves all the payment terms options that will populate the payment terms list in invoicing.html and quoting.html      
def get_payment_terms(request):
    PAYMENT_TERMS_CHOICES = [
        {'value': 'Net30', 'display': 'Net 30 Days'},
        {'value': 'Net60', 'display': 'Net 60 Days'},
        {'value': 'NetEOM', 'display': 'Net End of Month'},
    ]
    return JsonResponse(PAYMENT_TERMS_CHOICES, safe=False)

# Retrieves all the states options that will populate the states list in invoicing.html and quoting.html 
def get_states(request):
    BILLING_ADDRESS_STATE_OPTIONS = [
        {'value': 'QLD', 'display': 'QLD'},
        {'value': 'NSW', 'display': 'NSW'},
        {'value': 'VIC', 'display': 'VIC'},
        {'value': 'WA', 'display': 'WA'},
        {'value': 'SA', 'display': 'SA'},
        {'value': 'NT', 'display': 'NT'},
        {'value': 'TAS', 'display': 'TAS'},
        {'value': 'ACT', 'display': 'ACT'},
    ]
    return JsonResponse(BILLING_ADDRESS_STATE_OPTIONS, safe=False)

# Generates a basic pdf for the invoice based on invoice id in the invoice_viewer.html page.
def generate_invoice_pdf(invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        line_items = LineItem.objects.filter(invoice=invoice)
    except Invoice.DoesNotExist:
        return None
    
    invoice_info = [
        ["Invoice ID", str(invoice.id)],
        ["Date", str(invoice.date)],
        ["Client", str(invoice.client.name)],
        ["Shipping", str(invoice.shipping)],
        ["Discount", str(invoice.discount)],
        ["Tax", str(invoice.tax)],
        ["Sub-total", str(invoice.sub_total)],
        ["Total-amount", str(invoice.total_amount)],
    ]
    
    data = [["Description", "Quantity", "Unit Price", "Total"]]
    for item in line_items:
        data.append([
            item.description,
            item.quantity,
            item.unit_price,
            item.line_total,
        ])
    
    pdf_buffer = BytesIO()
    pdf = SimpleDocTemplate(
        pdf_buffer,
        pagesize = letter
    )

    elements =[]

    invoice_table = Table(invoice_info)
    elements.append(invoice_table)
    elements.append(Spacer(1, 0.25 * inch))

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)

    pdf.build(elements)
    pdf_data = pdf_buffer.getvalue()
    pdf_buffer.close()

    return pdf_data

# Creates a downloadable file that the user can download from the invoice_viewer.html page
@login_required
def get_invoice_pdf(request, invoice_id):
    pdf_data = generate_invoice_pdf(invoice_id)

    if pdf_data is None:
        return HttpResponse('Invoice not found', status=404)
    
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_id}.pdf"'
    response.write(pdf_data)

    return response

# Sends the invoice pdf to the client the invoice is associated with
# Also formats the email with a clickable link using a token. Once the email is sent, the invoice is marked as 'PENDING'
@login_required
def send_invoice_email(request, invoice_id):
    if request.method == 'POST':
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            client_email = invoice.client.email
        except Invoice.DoesNotExist:
            return JsonResponse({'status': 'Invoice does not exist.'})
        
        try:
            pdf_data = generate_invoice_pdf(invoice_id)
        except Exception as e:
            return JsonResponse({'status': f'PDF generation failed: {str(e)}'})

        token = InvoiceActionToken.objects.create(invoice=invoice)
        button_url = urljoin(
            'http://127.0.0.1:8000',
            reverse('invoicing:invoice_as_paid', args=[str(token.token)])
        )

        subject = 'Your Invoice'
        text_content = 'Here is your invoice.'
        html_content = f'Here is your invoice. <a href="{button_url}">Mark as Paid</a>'
        from_email = 'testbot.orefox@gmail.com'
        to = [client_email]

        # Create and send email
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.attach('invoice.pdf', pdf_data, 'application/pdf')

        try:
            msg.send()
            invoice.status = 'PENDING'
            invoice.save()
        except Exception as e:
            return JsonResponse({'status': f'Email sending failed: {str(e)}'})

        return HttpResponseRedirect(reverse('invoicing:invoicing'))
    else:
        return JsonResponse({'status': 'Only POST method is allowed.'})

# Once the link is clicked by the recipient the invoice is marked as 'PAID' in the database
def invoice_as_paid(request, token):
    try:
        action_token = InvoiceActionToken.objects.get(token=token)
        if action_token.is_used:
            return HttpResponse("This link has already been used.")
        
        invoice = action_token.invoice
        invoice.status = 'PAID'
        invoice.save()
        
        action_token.is_used = True
        action_token.save()
        
        return HttpResponse("Invoice marked as paid.")
    except InvoiceActionToken.DoesNotExist:
        return HttpResponse("Invalid token.")
    
