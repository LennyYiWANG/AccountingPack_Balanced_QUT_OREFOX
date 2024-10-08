import json
from urllib.parse import urljoin
from django.forms import ValidationError
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .forms import QuoteForm
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from .models import Quote, LineItem, QuoteActionToken
from invoicing.models import Client
from .forms import LineItemForm
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from decimal import Decimal
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer


# Create your views here.

# Renders the home page for quoting
@login_required
def quoting_menu(request):
    return render(request, 'quoting.html')

# Retrieve the specific quote from the database using the quote id and view the quote
@login_required
def view_quote(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)
    context = {
        'quote': quote,
    }
    return render(request, 'quote_viewer.html', context)

# Retrieves all quotes from the database along with their fields. Each field is approprattely formatted
@login_required
def get_quotes(request):
    quotes = Quote.objects.select_related('client').values('id', 'client__name','date', 'sub_total', 'shipping', 'discount', 'tax', 'total_amount', 'status')
    quote_list = list(quotes)
    for quote in  quote_list:
        quote['client'] = quote.pop('client__name')
        quote['date'] = quote['date'].strftime('%d/%m/%Y')
        if quote['discount'] != None:
            quote['discount'] = "{:.2f}%".format(quote['discount'])
        quote['sub_total'] = "${:.2f}".format(quote['sub_total'])
        if quote['shipping'] != None:
            quote['shipping'] = "${:.2f}".format(quote['shipping'])
        quote['tax'] = "${:.2f}".format(quote['tax'])
        quote['total_amount'] = "${:.2f}".format(quote['total_amount'])
    return JsonResponse({'data': quote_list})

# Retrieves only the status of the quote so that it can be determined what table it goes into in quoting.html
def get_quote_status(request, quote_id):
    try:

        quote = Quote.objects.get(pk=quote_id)
        quote_data = {
            'status': quote.status,
        }
        
        return JsonResponse(quote_data)
    
    except Quote.DoesNotExist:
        return JsonResponse({'error': 'Quote not found'}, status=404)

# Creates the quote and posts the data to the data base. Initiall only with four fields, as adding line items will populate the remaining fields.   
@login_required
def create_quote(request):
    print(request.POST)
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            if quote.shipping is None:
                quote.shipping = Decimal('0.00')
            if quote.discount is None:
                quote.discount = Decimal('0.00')
            quote.save()
            return JsonResponse({
                'success': True,
                'quote': {
                    'client': str(quote.client),
                    'date': str(quote.date),
                    'shipping': str(quote.shipping),
                    'discount': str(quote.discount),
                }
            })
        else:
            print(form.errors)
            return JsonResponse({'success': False, 'errors': form.errors})

# Retrieves the quote id and it's details for when a checkbox is checked and the edit button is clicked       
@login_required
def get_quote_id(request, quote_id):
    try:
        quote = Quote.objects.get(pk=quote_id)
        data = {
            'id': quote.id,
            'client': quote.client.id,
            'date': quote.date,
            'shipping': quote.shipping,
            'discount': quote.discount
        }
        return JsonResponse({'status': 'success', 'data': data})
    except Quote.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Quote not found'})

# Posts the updated data to the database based on which quote was being edited  
@login_required
def edit_quote(request):
    if request.method == 'POST':
        quote_id = request.POST.get('id')
        client_id = request.POST.get('client')
        
        try:
            quote = Quote.objects.get(pk=quote_id)
            client = get_object_or_404(Client, pk=client_id)
            
            quote.client = client

            date = request.POST.get('date')
            shipping = request.POST.get('shipping', '0.0')
            discount = request.POST.get('discount', '0.0')

            if shipping == "":
                shipping = '0.0'
            if discount == "":
                discount = '0.0'

            quote.date = date
            quote.shipping = Decimal(shipping)
            quote.discount = Decimal(discount)
            
            quote.save()

            return JsonResponse({'status': 'success', 'message': 'Quote updated successfully'})
        except Quote.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Quote not found'})
        except ValidationError:
            return JsonResponse({'status': 'error', 'message': 'Validation Error'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

# Deletes the quotes from the database based on what quotes where checked. If multiple were checked, a list of id's is populated.
@login_required
def delete_quotes(request):
    data = json.loads(request.body)
    quote_ids = data.get('quote_ids', [])
    if request.method == "POST":
        if quote_ids:
            if len(quote_ids) == 1:
                quote = get_object_or_404(Quote, id=quote_ids[0])
                quote.delete()
            else:
                Quote.objects.filter(id__in=quote_ids).delete()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'no ids'})
    else:
        return HttpResponse(status=405)

# Deletes the line items based on what line item checkboxes were checked. If multiple were checked, a list if id's is populated. 
@login_required
def delete_line_items(request):
    if request.method == 'POST':
        quote_id = request.POST.get('quote_id')
        ids_to_delete = request.POST.getlist('line_item_ids[]')
        line_items = LineItem.objects.filter(id__in=ids_to_delete, quote_id=quote_id)

        print("IDs to Delete:", ids_to_delete)
        print("Line Items to Delete:", line_items.query)

        deleted_count, _ = line_items.delete()

        if deleted_count > 0:
            quote = Quote.objects.get(pk=quote_id)
            quote.calculate_total()
            return JsonResponse({'status': 'success', 'message': 'Line items deleted successfully'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

# Retrives the line item based on id. When edit button is clicked in quote_viewer, the details to be edited are retrieved from the database.
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
        

# Posts the new line item to the database with the quote id it's associated with
@login_required
def add_line_item(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)
    quote.calculate_total()
    if request.method == 'POST':
        form = LineItemForm(request.POST)
        if form.is_valid(): 
            line_item = form.save(commit=False)
            line_item.quote = quote
            line_item.save()
            return JsonResponse({'success': True}, status=201)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# Retrieves all the line items from the database associated with a particular quote id so that the quote template is populated
@login_required
def get_line_items(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)
    line_items = serialize('json', LineItem.objects.filter(quote=quote))
    return JsonResponse({'line_items': line_items}) 
        
"""@login_required
def delete_quote(request, quote_id):
    if request.method == 'POST':
        quote = get_object_or_404(Quote, id=quote_id)
        quote.delete()
        return JsonResponse({'status': 'success'})
    else:
        return HttpResponse(status=405)"""

# Responsible for recalculating the totals each time a line item is added and retireves them from the database
def get_quote_totals(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)

    quote.calculate_total()

    sub_total = str(quote.sub_total)
    tax = str(quote.tax)
    total_amount = str(quote.total_amount)
    shipping = str(quote.shipping if quote.shipping else Decimal('0.00'))
    discount = str(quote.discount if quote.discount else Decimal('0.00'))

    return JsonResponse({
        'sub_total': sub_total,
        'tax': tax,
        'total_amount': total_amount,
        'shipping': shipping,
        'discount': discount,
    })

# Generates a basic pdf for the quote based on quote id in the quote_viewer.html page.
def generate_quote_pdf(quote_id):
    try:
        quote = Quote.objects.get(id=quote_id)
        line_items = LineItem.objects.filter(quote=quote)
    except Quote.DoesNotExist:
        return None
    
    quote_info = [
        ["Quote ID", str(quote.id)],
        ["Date", str(quote.date)],
        ["Client", str(quote.client.name)],
        ["Shipping", str(quote.shipping)],
        ["Discount", str(quote.discount)],
        ["Tax", str(quote.tax)],
        ["Sub-total", str(quote.sub_total)],
        ["Total-amount", str(quote.total_amount)],
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

    quote_table = Table(quote_info)
    elements.append(quote_table)
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

# Creates a downloadable file that the user can download from the quote_viewer.html page
@login_required
def get_quote_pdf(request, quote_id):
    pdf_data = generate_quote_pdf(quote_id)

    if pdf_data is None:
        return HttpResponse('Quote not found', status=404)
    
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="quote_{quote_id}.pdf"'
    response.write(pdf_data)

    return response

# Sends the quote pdf to the client the invoice is associated with
# Also formats the email with a clickable link using a token. Once the email is sent, the quote is marked as 'CONFIRMED'
@login_required
def send_quote_email(request, quote_id):
    if request.method == 'POST':
        try:
            quote = Quote.objects.get(id=quote_id)
            client_email = quote.client.email
        except Quote.DoesNotExist:
            return JsonResponse({'status': 'Quote does not exist.'})
        
        try:
            pdf_data = generate_quote_pdf(quote_id)
        except Exception as e:
            return JsonResponse({'status': f'PDF generation failed: {str(e)}'})

        token = QuoteActionToken.objects.create(quote=quote)
        button_url = urljoin(
            'http://127.0.0.1:8000',
            reverse('quoting:quote_as_paid', args=[str(token.token)])
        )

        subject = 'Your quote'
        text_content = 'Here is your quote.'
        html_content = f'Here is your quote. <a href="{button_url}">Mark as Confirmed</a>'
        from_email = 'testbot.orefox@gmail.com'
        to = [client_email]

        # Create and send email
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.attach('quote.pdf', pdf_data, 'application/pdf')

        try:
            msg.send()
            quote.save()
        except Exception as e:
            return JsonResponse({'status': f'Email sending failed: {str(e)}'})

        return HttpResponseRedirect(reverse('quoting:quoting'))
    else:
        return JsonResponse({'status': 'Only POST method is allowed.'})

# Once the link is clicked by the recipient the quote is marked as 'PAID' in the database   
def quote_as_paid(request, token):
    try:
        action_token = QuoteActionToken.objects.get(token=token)
        if action_token.is_used:
            return HttpResponse("This link has already been used.")
        
        quote = action_token.quote
        quote.status = 'CONFIRMED'
        quote.save()
        
        action_token.is_used = True
        action_token.save()
        
        return HttpResponse("Quote marked as confirmed.")
    except QuoteActionToken.DoesNotExist:
        return HttpResponse("Invalid token.")
