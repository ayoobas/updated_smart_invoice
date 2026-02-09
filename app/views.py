from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from .models import Cropitem, Invoice, CustomerInfo
from django.utils import timezone
from django.core.files.base import ContentFile
import base64
import uuid
from django.db import IntegrityError
from django.http import JsonResponse
from django.db.models import Q

#To load the rates and display them
def home(request):
    items = Cropitem.objects.all()
    context = {
            'items':items
    }
    return render(request, 'index.html', context)

#To capture next purchase
def regcustomer(request):
    if request.method == "POST":
        # 1. Collect Data from Form
        fname = request.POST.get("fname")
        address = request.POST.get("address")
        phoneno = request.POST.get("phoneno")
        email = request.POST.get("email")
        signature_data = request.POST.get("signature_data")

        # 2. Handle Digital Signature
        signature_file = None
        if signature_data and "base64," in signature_data:
            try:
                format, imgstr = signature_data.split('base64,')
                ext = format.split('/')[-1].split(';')[0] 
                signature_file = ContentFile(
                    base64.b64decode(imgstr), 
                    name=f"signature_{uuid.uuid4().hex[:6]}.{ext}"
                )
            except Exception as e:
                print(f"Error decoding signature: {e}")
                #for crop items

            items = Cropitem.objects.all()
            context = {
            'items':items
                }

        # 3. Save to Database
        try:
            CustomerInfo.objects.create(
                name=fname, 
                address=address, 
                phone_no=phoneno, 
                email=email,
                image=signature_file
            )
            messages.success(request, "✅ Records saved successfully!")
           
            return redirect('new_customer')
            
            
        except IntegrityError:
            messages.warning(request, "This Email or Phone Number is already registered.")
        except Exception as e:
            messages.error(request, f"Database Error: {e}")

    return render(request, "index.html")

#to search for customer information 
def search_customer(request):
    query = request.GET.get('query', '')
    customer = CustomerInfo.objects.filter(Q(email=query) | Q(phone_no=query)).first()

    if customer:
        return JsonResponse({
            'success': True,
            'id': customer.id, # Send the ID to the frontend
            'name': customer.name,
            'address': customer.address,
            'phone': customer.phone_no,
            'email': customer.email,
        })
    
    return JsonResponse({'success': False})




def generate_invoice(request):
    if request.method == "POST":
        # 1. Capture Quantities (Default to 0 if empty)
        customer_id = request.POST.get("customer_id")
        print("customerid", customer_id)
        
        qty_tomatoes = int(request.POST.get("Tomatoes") or 0)
        qty_bell_pepper = int(request.POST.get("Bell_Pepper") or 0)
        qty_cucumber = int(request.POST.get("Cucumber") or 0)
        qty_habanero = int(request.POST.get("Abanero") or 0) # Check spelling vs template
        discount = int(request.POST.get("discount") or 0)
        createdate = request.POST.get("createdate")

        # 2. Check if total items are greater than 0
        if sum([qty_tomatoes, qty_bell_pepper, qty_cucumber, qty_habanero]) == 0:
            messages.warning(request, "Error: You must enter at least one item quantity.")
            return render(request, 'index.html', {'items': Cropitem.objects.all()})

        # 3. Dynamic Price Calculation
        items_in_db = Cropitem.objects.all()
        rates = {item.name: item.rate for item in items_in_db}

        # Be careful: dictionary keys must match the name in your Cropitem table exactly
        subtotal = (
            (qty_tomatoes * rates.get('Tomatoes', 0)) +
            (qty_bell_pepper * rates.get('Bell_Pepper', 0)) +
            (qty_cucumber * rates.get('Cucumber', 0)) +
            (qty_habanero * rates.get('Abanero', 0))
        )
        final_total = subtotal - discount

        # 4. Save to Invoice Model
        try:
            new_invoice = Invoice.objects.create(
                customer_id=customer_id,
                tomatoes=qty_tomatoes,
                bell_pepper=qty_bell_pepper,
                cucumber=qty_cucumber,
                abernero=qty_habanero, # Ensure this matches your Model field name
                discount=discount,
                total_price=final_total,
                created_at=createdate if createdate else timezone.now().date()
            )
            messages.success(request, "✅ Records saved successfully!")
            return redirect('view_invoice', pk=new_invoice.pk)
            
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            print("error",e)
            # Optional: print(e) to see the error in your terminal

    # GET Request: Load items for the table and show the form
    items = Cropitem.objects.all()
    return render(request, 'index.html', {'items': items})

#To view the invoice generated

def view_invoice(request, pk):
    # This fetches only ONE invoice by its ID, or shows a 404 error if not found
    items_in_db = Cropitem.objects.all()
    rates = {item.name: item.rate for item in items_in_db}
    rate_t = rates.get('Tomatoes', 0)
    rate_b =  rates.get('Bell_Pepper', 0)
    rate_c = rates.get('Cucumber', 0)
    rate_a = rates.get('Abanero', 0)

    invoice = get_object_or_404(Invoice, pk=pk)

    print('invoice',invoice)
    
    context = {
        'invoice': invoice,
        'rate_t':rate_t,
        'rate_b':rate_b,
        'rate_c':rate_c,
        'rate_a':rate_a
    }
    return render(request, 'success.html', context)



