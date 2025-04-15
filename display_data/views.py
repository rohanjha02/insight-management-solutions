from django.shortcuts import render, redirect
import firebase_admin
from firebase_admin import credentials, db

def home(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        users_ref = db.reference("users").get()
        
        if users_ref:
            for user_id, user_data in users_ref.items():
                if user_data.get("email") == email and user_data.get("password") == password and user_data.get("role") == "admin":
                    return redirect("insight_management_solutions")
        
        return render(request, "display_data/home.html", {"error_message": "Invalid Credentials or Not an Admin"})
    
    return render(request, "display_data/home.html")



import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from firebase_admin import db
from datetime import datetime

# View to fetch and filter sales data
def sales_page(request):
    ref = db.reference('customers')  # Firebase node for sales
    data = ref.get() or {}

    # Extract unique values for dropdown filters
    all_customers = {value.get('CUSTOMER', '').strip() for value in data.values() if 'CUSTOMER' in value}
    all_districts = {value.get('DISTRICT', '').strip() for value in data.values() if 'DISTRICT' in value}
    all_branch_codes = {value.get('Branch_code', '').strip() for value in data.values() if 'Branch_code' in value}

    # Get filter values from request
    selected_customer = request.GET.get('customer', 'all')
    selected_district = request.GET.get('district', 'all')
    selected_branch_code = request.GET.get('branch_code', 'all')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')

    # Convert date strings to datetime objects
    from_date_obj = datetime.strptime(from_date, '%Y-%m-%d') if from_date else None
    to_date_obj = datetime.strptime(to_date, '%Y-%m-%d') if to_date else None

    filtered_data = {}

    for key, value in data.items():
        amc_due_date_str = value.get('AMC_due', '').strip()
        amc_due_date = None

        try:
            if amc_due_date_str:
                amc_due_date = datetime.strptime(amc_due_date_str, '%d-%m-%Y')
        except ValueError:
            amc_due_date = None  # Skip invalid dates

        # Apply filters
        if (
            (selected_customer == 'all' or value.get('CUSTOMER', '').strip().lower() == selected_customer.lower()) and
            (selected_district == 'all' or value.get('DISTRICT', '').strip().lower() == selected_district.lower()) and
            (selected_branch_code == 'all' or value.get('Branch_code', '').strip().lower() == selected_branch_code.lower()) and
            (not from_date_obj or (amc_due_date and amc_due_date >= from_date_obj)) and
            (not to_date_obj or (amc_due_date and amc_due_date <= to_date_obj))
        ):
            filtered_data[key] = value

    context = {
        'data': filtered_data,
        'selected_customer': selected_customer,
        'selected_district': selected_district,
        'selected_branch_code': selected_branch_code,
        'from_date': from_date,
        'to_date': to_date,
        'all_customers': sorted(all_customers),
        'all_districts': sorted(all_districts),
        'all_branch_codes': sorted(all_branch_codes),
    }

    return render(request, 'display_data/sales.html', context)



import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from firebase_admin import db
from datetime import datetime


# View to fetch and filter data
def get_firebase_data(request):
    ref = db.reference('customers')  # Firebase node
    data = ref.get() or {}  # Fetch the data (handle empty case)

    # Extract unique values for dropdown filters
    all_customers = {value.get('CUSTOMER', '').strip() for value in data.values() if 'CUSTOMER' in value}
    all_districts = {value.get('DISTRICT', '').strip() for value in data.values() if 'DISTRICT' in value}
    all_branch_codes = {value.get('Branch_code', '').strip() for value in data.values() if 'Branch_code' in value}

    # Get filter values from request
    selected_customer = request.GET.get('customer', 'all')
    selected_district = request.GET.get('district', 'all')
    selected_branch_code = request.GET.get('branch_code', 'all')
    from_date = request.GET.get('from_date', '')  # Expected format: YYYY-MM-DD
    to_date = request.GET.get('to_date', '')

    # Convert date strings to datetime objects (if provided)
    from_date_obj = datetime.strptime(from_date, '%Y-%m-%d') if from_date else None
    to_date_obj = datetime.strptime(to_date, '%Y-%m-%d') if to_date else None

    filtered_data = {}

    for key, value in data.items():
        amc_due_date_str = value.get('AMC_due', '').strip()
        amc_due_date = None

        # Convert AMC_due from "DD-MM-YYYY" to datetime
        try:
            if amc_due_date_str:
                amc_due_date = datetime.strptime(amc_due_date_str, '%d-%m-%Y')
        except ValueError:
            amc_due_date = None  # Skip invalid dates

        # Apply filters
        if (
            (selected_customer == 'all' or value.get('CUSTOMER', '').strip().lower() == selected_customer.lower()) and
            (selected_district == 'all' or value.get('DISTRICT', '').strip().lower() == selected_district.lower()) and
            (selected_branch_code == 'all' or value.get('Branch_code', '').strip().lower() == selected_branch_code.lower()) and
            (not from_date_obj or (amc_due_date and amc_due_date >= from_date_obj)) and
            (not to_date_obj or (amc_due_date and amc_due_date <= to_date_obj))
        ):
            filtered_data[key] = value  # Add record to filtered data

    context = {
        'data': filtered_data,
        'selected_customer': selected_customer,
        'selected_district': selected_district,
        'selected_branch_code': selected_branch_code,
        'from_date': from_date,
        'to_date': to_date,
        'all_customers': sorted(all_customers),
        'all_districts': sorted(all_districts),
        'all_branch_codes': sorted(all_branch_codes),
    }

    return render(request, 'display_data/data_display.html', context)

import csv
import re
from django.http import HttpResponse
from firebase_admin import db

def normalize_text(text):
    """Normalize text: lowercase, strip spaces, and remove extra spaces"""
    return re.sub(r'\s+', ' ', text.strip().lower()) if text else ""

def download_csv(request):
    ref = db.reference('customers')
    data = ref.get() or {}

    # Debugging: Print all received GET parameters
    print(f"Received GET parameters: {request.GET}")

    # Fetch filter values correctly
    raw_branch_code = request.GET.get('branch_code', '')
    raw_customer_name = request.GET.get('customer', '')  # FIXED PARAMETER NAME

    # Normalize input values
    selected_branch_code = normalize_text(raw_branch_code)
    selected_customer_name = normalize_text(raw_customer_name)

    # Debugging: Check normalization
    print(f"Normalized Branch Code: {selected_branch_code}, Normalized Customer Name: {selected_customer_name}")

    filter_type = request.GET.get('filter_type', 'and').strip().lower()  # Default to "and"

    print(f"CSV Download Requested - Branch: {selected_branch_code}, Customer: {selected_customer_name}, Filter Type: {filter_type}")

    # Apply filters correctly (ensure only "Billed" records are included)
    filtered_data = []
    for key, record in (data or {}).items():
        if record.get("status") == "Billed":  # Only include "Billed" invoices
            branch_code = normalize_text(record.get("branch_code", ""))
            customer_name = normalize_text(record.get("party_cb", ""))  # Ensure it matches the correct field

            # Debugging: Print each record being checked
            print(f"Checking Record - Branch: {branch_code}, Customer: {customer_name}")

            branch_match = (selected_branch_code == '' or branch_code == selected_branch_code)
            customer_match = (selected_customer_name == '' or customer_name == selected_customer_name)

            if (filter_type == 'and' and branch_match and customer_match) or \
               (filter_type == 'or' and (branch_match or customer_match)) or \
               (selected_branch_code == '' and selected_customer_name == ''):
                filtered_data.append(record)

    print(f"Filtered Records Count for CSV: {len(filtered_data)}")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_data.csv"'

    writer = csv.writer(response)
    headers = ["customer_name", "branch_code", "machine_serial_number", "machine_type", "model",
               "state", "district", "billing_address", "mobile_number", "pi_date",
               "pi_no", "quantity", "total_bill_amount", "reference_by", "warranty_date",
               "amc", "frequency", "amc_due_date", "amc_amount", "remarks"]
    writer.writerow(headers)

    for record in filtered_data:
        writer.writerow([
            record.get("party_cb", "N/A"),  # Ensure this field matches customer name
            record.get("branch_code", "N/A"),
            record.get("machine_serial_number", "N/A"),
            record.get("machine_type", "N/A"),
            record.get("model", "N/A"),
            record.get("state", "N/A"),
            record.get("district", "N/A"),
            record.get("billing_address", "N/A"),
            record.get("mobile_number", "N/A"),
            record.get("pi_date", "N/A"),
            record.get("pi_no", "N/A"),
            record.get("quantity", "N/A"),
            record.get("total_bill_amount", "N/A"),
            record.get("reference_by", "N/A"),
            record.get("warranty_date", "N/A"),
            record.get("amc", "No"),
            record.get("frequency", ""),
            record.get("amc_due_date", "N/A"),
            record.get("amc_amount", "0"),
            record.get("remarks", "")
        ])

    return response



# View to add a new record
def add_data(request):
    if request.method == 'POST':
        new_data = {
            'ADDRESS': request.POST.get('ADDRESS', ''),
            'AMC_amount': request.POST.get('AMC_amount', ''),
            'AMC_due': request.POST.get('AMC_due', ''),  # Ensure correct format
            'AMC_mode': request.POST.get('AMC_mode', ''),
            'Branch_code': request.POST.get('Branch_code', ''),
            'CUSTOMER': request.POST.get('CUSTOMER', ''),
            'DISTRICT': request.POST.get('DISTRICT', ''),
            'Due_month': request.POST.get('Due_month', ''),
            'MODEL': request.POST.get('MODEL', ''),
            'P_GROUP': request.POST.get('P_GROUP', ''),
            'QTY': request.POST.get('QTY', ''),
            'Serial_number': request.POST.get('Serial_number', ''),
            'State': request.POST.get('State', ''),
            'Status': request.POST.get('Status', ''),
            'Total_amc_amt': request.POST.get('Total_amc_amt', ''),
            'contact': request.POST.get('contact', ''),
            'date_of_installation': request.POST.get('date_of_installation', ''),
            'inv_date': request.POST.get('inv_date', ''),
            'invoice_no': request.POST.get('invoice_no', ''),
            'engineer_name': request.POST.get('engineer_name', ''),
        }
        
        # Add new data to Firebase
        db.reference('customers').push(new_data)

        return redirect('get_firebase_data')

    return render(request, 'display_data/add_data.html')


from django.shortcuts import render, redirect
from firebase_admin import db

def edit_data(request, record_key): 
    ref = db.reference(f'customers/{record_key}')
    record = ref.get()

    if not record:
        return redirect('sale')  # Redirect if record not found

    if request.method == 'POST':
        updated_data = {
            'party_cb': request.POST.get('party_cb', ''),
            'branch_code': request.POST.get('branch_code', ''),
            'machine_serial_number': request.POST.get('machine_serial_number', ''),
            'machine_type': request.POST.get('machine_type', ''),
            'model': request.POST.get('model', ''),
            'state': request.POST.get('state', ''),
            'pincode': request.POST.get('pincode', ''),
            'district': request.POST.get('district', ''),
            'billing_address': request.POST.get('billing_address', ''),
            'mobile_number': request.POST.get('mobile_number', ''),
            'email': request.POST.get('email', ''),
            'pi_date': request.POST.get('pi_date', ''),
            'pi_no': request.POST.get('pi_no', ''),
            'quantity': request.POST.get('quantity', ''),
            'total_bill_amount': request.POST.get('total_bill_amount', ''),
            'reference_by': request.POST.get('reference_by', ''),
        }
        
        # Update the record in Firebase
        ref.update(updated_data)

        return redirect('sale')

    context = {'record': record}
    return render(request, 'display_data/edit_data.html', context) 


def upcoming_amc(request):
    # Initialize all_months here to ensure it is always defined
    all_months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    # Reference to the Firebase database
    ref = db.reference('customers')  # Adjust the path as needed
    data = ref.get()  # Fetch data from Firebase

    if not data:
        print("No data found in Firebase.")  # Debugging print statement
    else:
        print(f"Data fetched: {data}")  # Debugging print statement

    current_date = datetime.now()
    upcoming_amc_payments = []

    try:
        # Loop through each customer to calculate AMC payments
        for customer in data.values():  # Assuming data is a dictionary of customers
            invoice_no = customer.get('invoice_no')  # Using invoice_no for identification
            amc_due_str = customer.get('AMC_due')  # AMC_due should be in 'DD-MM-YY' format
            amc_mode = customer.get('AMC_mode', '').strip().lower()  # AMC mode, case-insensitive

            print(f"Processing customer: {invoice_no}, AMC_due: {amc_due_str}, AMC_mode: {amc_mode}")  # Debugging print statement

            if invoice_no and amc_due_str and amc_mode:
                try:
                    # Convert AMC_due to datetime format
                    amc_due_date = datetime.strptime(amc_due_str, '%d-%m-%Y')  # Update format to '%d-%m-%Y'

                    # Determine the upcoming AMC payment date based on AMC_mode
                    if amc_mode == "yearly":
                        # Calculate the upcoming AMC payment date (1 year after AMC_due)
                        upcoming_amc_date = amc_due_date + relativedelta(years=1)
                    elif amc_mode == "half-yearly":
                        # Calculate the upcoming AMC payment date (6 months after AMC_due)
                        upcoming_amc_date = amc_due_date + relativedelta(months=6)
                    else:
                        # Skip if AMC_mode is not recognized
                        print(f"Skipping customer {invoice_no} due to unrecognized AMC_mode: {amc_mode}")
                        continue

                    # Only include payments for the current year
                    if current_date <= upcoming_amc_date < current_date.replace(year=current_date.year + 1):
                        upcoming_amc_payments.append({
                            'invoice_no': invoice_no,
                            'amc_due_date': upcoming_amc_date.strftime('%d-%m-%Y'),
                            'month': upcoming_amc_date.strftime('%B'),
                            'address': customer.get('ADDRESS'),
                            'amc_amount': customer.get('AMC_amount'),
                            'amc_mode': customer.get('AMC_mode'),
                            'branch_code': customer.get('Branch_code'),
                            'customer': customer.get('CUSTOMER'),
                            'district': customer.get('DISTRICT'),
                            'engineer_name': customer.get('engineer_name'),  # Added engineer_name
                            'due_month': customer.get('Due_month'),
                            'model': customer.get('MODEL'),
                            'p_group': customer.get('P_GROUP'),
                            'qty': customer.get('QTY'),
                            'serial_number': customer.get('Serial_number'),
                            'state': customer.get('State'),
                            'status': customer.get('Status'),
                            'total_amc_amt': customer.get('Total_amc_amt'),
                            'contact': customer.get('contact'),
                            'date_of_installation': customer.get('date_of_installation'),
                            'inv_date': customer.get('inv_date'),
                        })
                except ValueError as e:
                    print(f"Error parsing AMC_due for {invoice_no}: {e}")

        # Group the payments by month for display
        payments_by_month = {}
        for entry in upcoming_amc_payments:
            month = entry['month']
            if month not in payments_by_month:
                payments_by_month[month] = []
            payments_by_month[month].append(entry)

        # Ensure all months appear even if they have no payments
        for month in all_months:
            if month not in payments_by_month:
                payments_by_month[month] = []

        # Get the selected month if available in the query params
        selected_month = request.GET.get('month', None)

        # Filter payments for the selected month, or show all months
        if selected_month:
            selected_amc_payments = payments_by_month.get(selected_month, [])
        else:
            selected_amc_payments = []

        # Check if any data exists
        if not upcoming_amc_payments:
            print("No upcoming AMC payments found.")  # Debugging print statement

        # Pass the data to the template
        return render(request, 'display_data/upcoming_amc.html', {
            'payments_by_month': payments_by_month,
            'selected_amc_payments': selected_amc_payments,
            'selected_month': selected_month,
            'current_date': current_date.strftime('%d-%m-%Y'),
            'all_months': all_months,
            'data': data,  # Pass raw data for inspection
            'error_message': "No data found." if not upcoming_amc_payments else "",  # Conditional error message
        })
    except Exception as e:
        print(f"Error processing AMC data: {e}")  # Debugging print statement
        return render(request, 'display_data/upcoming_amc.html', {
            'payments_by_month': {},  # Pass an empty dictionary if no data is available
            'selected_amc_payments': [],
            'selected_month': None,
            'current_date': current_date.strftime('%d-%m-%Y'),
            'all_months': all_months,  # Ensure all months are displayed even with no data
            'data': {},  # Pass an empty data object
            'error_message': "No data found."  # Optional message to display in the template
        })



from django.shortcuts import render
from firebase_admin import credentials, db
from datetime import datetime


def view_bill(request, invoice_no):
    # Reference to the Firebase database
    ref = db.reference('customers')  # Adjust the path as needed
    data = ref.get()  # Fetch data from Firebase

    if not data:
        print("No data found in Firebase.")  # Debugging print statement
        return render(request, 'display_data/view_bill.html', {
            'error_message': "No data found.",
        })

    # Try to find the customer details using the invoice_no
    payment_details = None
    for customer in data.values():
        if customer.get('invoice_no') == invoice_no:
            payment_details = {
                'invoice_no': customer.get('invoice_no'),
                'amc_due_date': customer.get('AMC_due'),
                'customer': customer.get('CUSTOMER'),
                'address': customer.get('ADDRESS'),
                'amc_amount': customer.get('AMC_amount'),
                'amc_mode': customer.get('AMC_mode'),
                'branch_code': customer.get('Branch_code'),
                'status': customer.get('Status'),
                'district': customer.get('DISTRICT'),
                'due_month': customer.get('Due_month'),
                'model': customer.get('MODEL'),
                'p_group': customer.get('P_GROUP'),
                'qty': customer.get('QTY'),
                'serial_number': customer.get('Serial_number'),
                'state': customer.get('State'),
                'total_amc_amt': customer.get('Total_amc_amt'),
                'contact': customer.get('contact'),
                'date_of_installation': customer.get('date_of_installation'),
                'inv_date': customer.get('inv_date'),
                'engineer_name': customer.get('engineer_name')
            }
            break

    # If no data is found for the provided invoice_no, show an error message
    if not payment_details:
        print(f"No details found for invoice: {invoice_no}")  # Debugging print statement
        return render(request, 'display_data/view_bill.html', {
            'error_message': "No payment details found for the given invoice number.",
        })

    # Pass the payment details to the template
    return render(request, 'display_data/view_bill.html', {
        'payment': payment_details,
    })


from django.shortcuts import render
from django.http import JsonResponse
import json
import firebase_admin
from firebase_admin import credentials, db

# Firebase DB Reference
ref = db.reference('products')

def product_details(request):
    # Fetch products from Firebase
    products = ref.get() or {}

    # Convert products into a list for easy handling in the template
    product_list = [{"id": key, **value} for key, value in products.items()]

    return render(request, 'display_data/product_details.html', {'products': product_list})



import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import firebase_admin
from firebase_admin import credentials, db

# Firebase DB Reference
ref = db.reference('products')

@csrf_exempt
def add_product(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            if not all(k in data for k in ("name", "description", "price", "image")):

                return JsonResponse({"error": "Missing required fields"}, status=400)
            
            new_product = {
                "name": data.get("name", "").strip(),
                "description": data.get("description", "").strip(),
                "price": data.get("price", "").strip(),
                "image": data.get("image", "").strip()  # Image field
            }

            ref.push(new_product)  # Add product to Firebase
            
            # Fetch updated product list after adding
            products = ref.get() or {}

            return JsonResponse({
                "message": "Product added successfully!",
                "products": [{"id": key, **value} for key, value in products.items()]
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)




from django.shortcuts import render
from firebase_admin import db
from datetime import datetime
from dateutil.relativedelta import relativedelta  # For accurate date calculations

def user_complaints(request):
    complaints_ref = db.reference('complaints')
    users_ref = db.reference('users')

    complaints_data = complaints_ref.get()
    users_data = users_ref.get()

    if not complaints_data:
        return render(request, 'display_data/user_complaints.html', {
            'error_message': "No complaints found."
        })

    pending_complaints = []
    resolved_complaints = []
    selected_month = request.GET.get('month', '')  
    selected_engineer = request.GET.get('engineer', '')  

    engineers = set()  

    for complaint in complaints_data.values():
        engineer_id = complaint.get('engineer_id')
        assigned_engineer = None
        if engineer_id and users_data and engineer_id in users_data:
            assigned_engineer = {
                'name': users_data[engineer_id].get('name'),
                'contact': users_data[engineer_id].get('contact'),
                'email': users_data[engineer_id].get('email'),
            }
            if assigned_engineer['name']:
                engineers.add(assigned_engineer['name'])

        created_at = complaint.get('createdAt', '')  
        created_date = created_at.split('T')[0] if 'T' in created_at else created_at  

        complaint_entry = {
            'branch': complaint.get('branch'),
            'branch_code': complaint.get('branch_code'),
            'branch_name': complaint.get('branch_name'),
            'complaint_description': complaint.get('complaint_description'),
            'email': complaint.get('email'),
            'machine_type': complaint.get('machine_type'),
            'mobile_number': complaint.get('mobile_number'),
            'state': complaint.get('state'),
            'createdAt': created_date,
            'remarks': complaint.get('remarks'),
            'status': complaint.get('status'),
            'assigned_engineer': assigned_engineer,
        }

        if complaint_entry['status'] == 'Pending':
            pending_complaints.append(complaint_entry)
        elif complaint_entry['status'] == 'Resolved':
            if selected_month:
                complaint_month = created_date.split('-')[1] if created_date else ''
                if complaint_month == selected_month:
                    if not selected_engineer or (assigned_engineer and assigned_engineer['name'] == selected_engineer):
                        resolved_complaints.append(complaint_entry)

    months = [
        ('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
        ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
        ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ]

    return render(request, 'display_data/user_complaints.html', {
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'selected_month': selected_month,
        'selected_engineer': selected_engineer,
        'months': months,
        'engineers': sorted(engineers)
    })

def view_complaint_details(request):
    complaints_ref = db.reference('complaints')
    users_ref = db.reference('users')
    customers_ref = db.reference('customers')

    complaints_data = complaints_ref.get()
    users_data = users_ref.get()
    customers_data = customers_ref.get()

    if not complaints_data or not users_data or not customers_data:
        return render(request, 'display_data/view_complaint.html', {
            'error_message': "No data found.",
        })

    branch_code = request.GET.get('branch_code')
    machine_type = request.GET.get('machine_type')
    if not branch_code or not machine_type:
        return render(request, 'display_data/view_complaint.html', {
            'error_message': "Branch code and machine type are required.",
        })

    complaint_details = None
    for complaint_id, complaint in complaints_data.items():
        if complaint.get('branch_code') == branch_code and complaint.get('machine_type') == machine_type:
            complaint_details = {
                'complaint_id': complaint_id,
                'branch': complaint.get('branch'),
                'branch_code': complaint.get('branch_code'),
                'branch_name': complaint.get('branch_name'),
                'complaint_description': complaint.get('complaint_description'),
                'email': complaint.get('email'),
                'machine_type': complaint.get('machine_type'),
                'mobile_number': complaint.get('mobile_number'),
                'state': complaint.get('state'),
                'address': complaint.get('address'),
                'assigned_engineer_id': complaint.get('engineer_id'),
                'remarks': complaint.get('remarks'),
            }
            break

    if not complaint_details:
        return render(request, 'display_data/view_complaint.html', {
            'error_message': "Complaint not found for this branch code and machine type.",
        })

    assigned_engineer = None
    engineer_id = complaint_details.get('assigned_engineer_id')
    if engineer_id and engineer_id in users_data:
        assigned_engineer = {
            'name': users_data[engineer_id].get('name'),
            'contact': users_data[engineer_id].get('contact'),
            'email': users_data[engineer_id].get('email'),
        }

    amc_status_message = ""
    amc_due_date = None

    matched_customer = None
    for customer in customers_data.values():
        if customer.get('branch_code') == branch_code and customer.get('machine_type') == machine_type:
            matched_customer = customer
            amc_due_str = customer.get('amc_due_date')
            amc_mode = customer.get('frequency', 'Yearly').lower()
            if amc_due_str:
                try:
                    amc_due_date = datetime.strptime(amc_due_str, '%Y-%m-%d')
                    current_date = datetime.now()
                    
                    if amc_mode == 'yearly':
                        upcoming_amc_date = amc_due_date + relativedelta(years=1)
                    elif amc_mode == 'half-yearly':
                        upcoming_amc_date = amc_due_date + relativedelta(months=6)
                    else:
                        amc_status_message = f"Unknown AMC mode: {amc_mode}"
                        break
                    
                    if current_date <= upcoming_amc_date:
                        amc_status_message = "You come under AMC."
                    else:
                        amc_status_message = "Your complaint will not be considered as your AMC due date has passed."
                except ValueError as e:
                    amc_status_message = "Invalid AMC due date format."
            break

    if not matched_customer:
        return render(request, 'display_data/view_complaint.html', {
            'error_message': "No registered appliance under your name.",
        })

    return render(request, 'display_data/view_complaint.html', {
        'complaint': complaint_details,
        'assigned_engineer': assigned_engineer,
        'amc_due_date': upcoming_amc_date.strftime('%d-%m-%Y') if amc_due_date else None,
        'amc_status_message': amc_status_message,
    })



from django.shortcuts import render

def agreement_form(request):
    return render(request, 'display_data/agreement_form.html')

def agreement(request):
    if request.method == "POST":
        reason = request.POST.get('reason')
        bank_name = request.POST.get('bank_name')
        model = request.POST.get('model')
        amc_start_date = request.POST.get('amc_start_date')
        amc_end_date = request.POST.get('amc_end_date')
        amc_amount = request.POST.get('amc_amount')

        context = {
            'reason': reason,
            'bank_name': bank_name,
            'model': model,
            'amc_start_date': amc_start_date,
            'amc_end_date': amc_end_date,
            'amc_amount': amc_amount
        }
        return render(request, 'display_data/agreement.html', context)
    
    return render(request, 'display_data/agreement_form.html')


from django.shortcuts import render, redirect
from django.http import JsonResponse
import firebase_admin
from firebase_admin import db
import json  # Import json to handle string parsing

def proforma_invoice(request):
    ref = db.reference('customers')

    if request.method == "POST":
        data = {
            "party_cb": request.POST.get("party_cb"),
            "select_customers": request.POST.get("select_customers"),
            "pi_date": request.POST.get("pi_date"),
            "pi_no": request.POST.get("pi_no"),
            "shipping_address": request.POST.get("shipping_address"),
            "billing_address": request.POST.get("billing_address"),
            "district": request.POST.get("district"),  # New field
            "state": request.POST.get("state"),  # New field
            "pincode": request.POST.get("pincode"),
            "interest_rate": request.POST.get("interest_rate"),
            "billing_currency": request.POST.get("billing_currency"),
            "convert_to_currency": request.POST.get("convert_to_currency"),
            "currency_rate": request.POST.get("currency_rate"),
            "po_date": request.POST.get("po_date"),
            "po_no": request.POST.get("po_no"),
            "normal_invoice": request.POST.get("normal_invoice", "off") == "on",
            "export_invoice": request.POST.get("export_invoice", "off") == "on",
            "item_service_detail": request.POST.get("item_service_detail"),
            "barcode": request.POST.get("barcode"),
            "with_inventory": request.POST.get("with_inventory", "off") == "on",
            "without_inventory": request.POST.get("without_inventory", "off") == "on",
            "quantity": request.POST.get("quantity"),
            "discount": request.POST.get("discount"),
            "taxable_amt": request.POST.get("taxable_amt"),
            "tax_amount": request.POST.get("tax_amount"),
            "bill_discount": request.POST.get("bill_discount"),
            "organization_name": request.POST.get("organization_name"),
            "reference_type": request.POST.get("reference_type"),
            "reference_by": request.POST.get("reference_by"),
            "remark": request.POST.get("remark"),
            "round_off": request.POST.get("round_off"),
            "total_bill_amount": request.POST.get("total_bill_amount"),
            "status": request.POST.get("status", "Unbilled"),  # Default to "Unbilled"
            "branch_code": request.POST.get("branch_code"),  # New field
            "machine_serial_number": request.POST.get("machine_serial_number"),  # New field
            "machine_type": request.POST.get("machine_type"),  # New field
            "model": request.POST.get("model"),
            "mobile_number": request.POST.get("mobile_number"),
            "email": request.POST.get("email"),  # New field
        }

        ref.push(data)
        return redirect('proforma_invoice')

    saved_data = ref.get()

    # Fix: Ensure data is correctly parsed from Firebase
    data_list = []
    if saved_data:
        for k, v in saved_data.items():
            if isinstance(v, str):  # Check if the value is a string
                try:
                    v = json.loads(v)  # Attempt to parse JSON
                except json.JSONDecodeError:
                    pass  # Keep as string if it's not valid JSON
            if isinstance(v, dict):  # Ensure it is a dictionary
                data_list.append({"key": k, **v})

    return render(request, 'display_data/proforma_invoice.html', {'data_list': data_list})



def update_status(request):
    if request.method == "POST":
        pi_no = request.POST.get("pi_no")
        new_status = request.POST.get("status")

        ref = db.reference('customers')
        saved_data = ref.get()

        if saved_data:
            for key, value in saved_data.items():
                if value.get("pi_no") == pi_no:
                    ref.child(key).update({"status": new_status})
                    return JsonResponse({"success": True})

    return JsonResponse({"success": False})


from django.shortcuts import render
from firebase_admin import db

def sale_page(request):
    # Reference to the "customers" node in Firebase
    proforma_ref = db.reference('customers')

    # Fetch all Pro Forma data
    proforma_data = proforma_ref.get()

    # Extract unique branch codes and customer names for dropdown filters
    all_branch_codes = {data.get("branch_code", "").strip() for data in proforma_data.values() if "branch_code" in data and data.get("branch_code")} if proforma_data else set()
    all_customer_names = {data.get("party_cb", "").strip() for data in proforma_data.values() if "party_cb" in data and data.get("party_cb")} if proforma_data else set()

    # Remove empty or None values
    all_branch_codes.discard("")
    all_customer_names.discard("")

    # Get filter values from request
    selected_branch_code = request.GET.get('branch_code', '').strip().lower()
    selected_customer_name = request.GET.get('customer_name', '').strip().lower()
    filter_type = request.GET.get('filter_type', 'and').strip().lower()  # "and" or "or" (default is "and")

    # Ensure data exists and filter only "Billed" Pro Forma invoices
    billed_proformas = []
    if proforma_data:
        for key, data in proforma_data.items():
            if data.get("status") == "Billed":
                branch_code = data.get("branch_code", "").strip().lower()
                customer_name = data.get("party_cb", "").strip().lower()

                branch_match = selected_branch_code == '' or branch_code == selected_branch_code
                customer_match = selected_customer_name == '' or customer_name == selected_customer_name

                # **✅ Attach `record_key` to each data dictionary**
                data["record_key"] = key

                # Apply AND/OR filtering correctly
                if filter_type == 'and' and (branch_match and customer_match):
                    billed_proformas.append(data)
                elif filter_type == 'or' and (branch_match or customer_match):
                    billed_proformas.append(data)
                elif selected_branch_code == '' and selected_customer_name == '':
                    billed_proformas.append(data)  # Show all if no filters

    return render(request, 'display_data/sale.html', {
        'data_list': billed_proformas,
        'all_branch_codes': sorted(all_branch_codes),
        'selected_branch_code': selected_branch_code,
        'all_customers': sorted(all_customer_names),
        'selected_customer': selected_customer_name,
        'filter_type': filter_type
    })






@csrf_exempt
def update_amc_details(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            record_key = data.get("record_key")

            if not record_key:
                return JsonResponse({"error": "Missing record key"}, status=400)

            proforma_ref = db.reference(f'customers/{record_key}')
            existing_data = proforma_ref.get()
            if not existing_data:
                return JsonResponse({"error": "Record not found"}, status=404)

            updates = {
                "warranty_date": data.get("warranty_date", ""),
                "amc": data.get("amc", "No"),
                "frequency": data.get("frequency", "Yearly"),
                "amc_due_date": data.get("amc_due_date", ""),
                "amc_amount": data.get("amc_amount", "0"),
            }
            
            # Condition to reset remarks, date_of_payment, bill_no, and utr_no if AMC due date changes
            if "amc_due_date" in data and data["amc_due_date"] != existing_data.get("amc_due_date"):
                updates["remarks"] = ""
                updates["date_of_payment"] = ""
                updates["bill_no"] = ""
                updates["utr_no"] = ""  # Reset UTR number as well
            
            # Allow manual update of remarks
            elif "remarks" in data:
                updates["remarks"] = data["remarks"]

            proforma_ref.update(updates)
            return JsonResponse({"success": True, "message": "AMC and warranty details updated successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=400)



from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
import json
import firebase_admin
from firebase_admin import db
from dateutil.relativedelta import relativedelta
from django.views.decorators.csrf import csrf_exempt

def amc_details(request):
    all_months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    current_date = datetime.today()
    current_year = current_date.year
    ref = db.reference('customers')
    data = ref.get()

    if not data:
        return render(request, 'display_data/amc.html', {
            'amc_records': [],
            'payments_by_month': {},
            'all_months': all_months,
            'selected_month': None,
            'error_message': "No AMC records found."
        })

    amc_records = []
    payments_by_month = {month: [] for month in all_months}

    try:
        for key, record in data.items():
            if record.get('amc') == "Yes":
                amc_due_date = record.get('amc_due_date')
                frequency = record.get('frequency', 'Yearly').lower()
                
                if amc_due_date:
                    try:
                        amc_date_obj = datetime.strptime(amc_due_date, '%Y-%m-%d')
                        
                        # Apply frequency to get upcoming due date
                        if frequency == 'yearly':
                            amc_date_obj += relativedelta(years=1)
                        elif frequency == 'half-yearly':
                            amc_date_obj += relativedelta(months=6)
                        
                        # Only include upcoming AMC within this year
                        if current_date <= amc_date_obj <= datetime(current_year, 12, 31):
                            record['amc_due_date'] = amc_date_obj
                            record['month'] = all_months[amc_date_obj.month - 1]
                            record['record_key'] = key  # Store record key for updates
                            amc_records.append(record)
                    except ValueError:
                        continue

        amc_records.sort(key=lambda x: x.get('amc_due_date', datetime.max))

        for record in amc_records:
            month_name = record['month']
            payments_by_month[month_name].append(record)

        selected_month = request.GET.get('month', None)
        selected_amc_records = payments_by_month.get(selected_month, []) if selected_month else []

        return render(request, 'display_data/amc.html', {
            'amc_records': amc_records,
            'payments_by_month': payments_by_month,
            'selected_amc_records': selected_amc_records,
            'all_months': all_months,
            'selected_month': selected_month,
        })
    except Exception as e:
        return render(request, 'display_data/amc.html', {
            'amc_records': [],
            'payments_by_month': {},
            'all_months': all_months,
            'selected_month': None,
            'error_message': f"Error fetching AMC details: {str(e)}"
        })

from django.shortcuts import render
from firebase_admin import db
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def update_amc_remarks(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            record_key = data.get("record_key")
            remarks = data.get("remarks")
            bill_no = data.get("bill_no")  # Get bill_no input
            utr_no = data.get("utr_no")  # Get UTR number input

            if not record_key:
                return JsonResponse({"error": "Missing record key"}, status=400)

            proforma_ref = db.reference(f'customers/{record_key}')
            record = proforma_ref.get()
            if not record:
                return JsonResponse({"error": "Record not found"}, status=404)

            update_data = {"remarks": remarks}
            current_date = datetime.today().strftime('%Y-%m-%d')
            
            # If remarks are "Paid", require bill_no and UTR_no and add date_of_payment
            if remarks.lower() == "paid":
                if not bill_no or not utr_no:
                    return JsonResponse({"error": "Missing bill number or UTR number"}, status=400)
                update_data.update({
                    "date_of_payment": current_date,
                    "bill_no": bill_no,
                    "utr_no": utr_no  # Store UTR number
                })
                
                # Save new "Paid" record to "amc_status" without overwriting existing ones
                amc_status_ref = db.reference("amc_status")
                new_entry = amc_status_ref.push({
                    "record_key": record_key,
                    "amc_amount": record.get("amc_amount", ""),
                    "amc_due_date": record.get("amc_due_date", ""),
                    "party_cb": record.get("party_cb", ""),
                    "branch_code": record.get("branch_code", ""), 
                    "machine_serial_number": record.get("machine_serial_number", ""), 
                    "machine_type": record.get("machine_type", ""), 
                    "billing_address": record.get("billing_address", ""),
                    "frequency": record.get("frequency", ""),
                    "remarks": "Paid",
                    "date_of_payment": current_date,
                    "bill_no": bill_no,
                    "utr_no": utr_no  # Store UTR number
                })

            proforma_ref.update(update_data)
            return JsonResponse({"success": True, "message": "Remarks updated successfully", "new_entry_key": new_entry.key if remarks.lower() == "paid" else None})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)


from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from firebase_admin import db

def amc_status(request):
    selected_remarks = request.GET.get("remarks", "").strip().lower()
    utr_no_filter = request.GET.get("utr_no", "").strip()
    selected_branch_code = request.GET.get("branch_code", "").strip().lower()
    selected_customer_name = request.GET.get("customer_name", "").strip().lower()
    filter_type = request.GET.get("filter_type", "and").strip().lower()

    amc_records = []
    current_date = datetime.today()
    current_year = current_date.year
    
    try:
        ref = None
        data = {}

        # Determine Firebase Reference Based on Remarks
        if selected_remarks == "paid":
            ref = db.reference("amc_status")
        elif selected_remarks == "unpaid":
            ref = db.reference("customers")
        
        # Fetch data safely
        if ref:
            fetched_data = ref.get()
            if fetched_data:
                data = fetched_data

        # Extract unique branch codes and customer names for dropdown filters
        all_branch_codes = {record.get("branch_code", "").strip() for record in data.values() if "branch_code" in record and record.get("branch_code")} if data else set()
        all_customer_names = {record.get("party_cb", "").strip() for record in data.values() if "party_cb" in record and record.get("party_cb")} if data else set()
        all_branch_codes.discard("")
        all_customer_names.discard("")

        # Process records if data exists
        for key, record in data.items():
            remarks = record.get("remarks", "").strip().lower()

            # Match records based on remarks
            if remarks == selected_remarks:
                amc_due_date = record.get("amc_due_date")
                frequency = record.get("frequency", "Yearly").strip().lower()

                if amc_due_date:
                    try:
                        amc_date_obj = datetime.strptime(amc_due_date, '%Y-%m-%d')

                        # Apply frequency rules correctly
                        if frequency == 'yearly':
                            amc_date_obj += relativedelta(years=1)
                        elif frequency == 'half-yearly':
                            amc_date_obj += relativedelta(months=6)

                        # Ensure AMC due date is within the current year
                        if current_date <= amc_date_obj <= datetime(current_year, 12, 31):
                            record['amc_due_date'] = amc_date_obj.strftime('%Y-%m-%d')
                            record["key"] = key

                            # Extract filters
                            branch_code = record.get("branch_code", "").strip().lower()
                            customer_name = record.get("party_cb", "").strip().lower()
                            record_utr_no = record.get("utr_no", "").strip()

                            # Apply individual filters
                            branch_match = selected_branch_code == '' or branch_code == selected_branch_code
                            customer_match = selected_customer_name == '' or customer_name == selected_customer_name
                            utr_match = utr_no_filter == '' or (selected_remarks == "paid" and utr_no_filter.lower() in record_utr_no.lower())

                            # Apply AND/OR filtering logic
                            if filter_type == 'and' and (branch_match and customer_match and utr_match):
                                amc_records.append(record)
                            elif filter_type == 'or' and (branch_match or customer_match or utr_match):
                                amc_records.append(record)
                            elif selected_branch_code == '' and selected_customer_name == '' and utr_no_filter == '':
                                amc_records.append(record)  # Show all if no filters

                    except ValueError:
                        continue  # Skip records with invalid dates

        return render(request, "display_data/amc_status.html", {
            "amc_records": amc_records, 
            "selected_remarks": selected_remarks,
            "utr_no_filter": utr_no_filter,
            "all_branch_codes": sorted(all_branch_codes),
            "selected_branch_code": selected_branch_code,
            "all_customers": sorted(all_customer_names),
            "selected_customer_name": selected_customer_name,
            "filter_type": filter_type
        })

    except Exception as e:
        return render(request, "display_data/amc_status.html", {
            "amc_records": [], 
            "selected_remarks": selected_remarks, 
            "utr_no_filter": utr_no_filter,
            "all_branch_codes": [],
            "selected_branch_code": selected_branch_code,
            "all_customers": [],
            "selected_customer_name": selected_customer_name,
            "filter_type": filter_type,
            "error_message": str(e)
        })





@csrf_exempt
def update_amc_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            record_key = data.get("key")
            bill_no = data.get("bill_no")
            utr_no = data.get("utr_no")  # Get UTR number input
            remarks = data.get("remarks", "")

            if not record_key:
                return JsonResponse({"success": False, "error": "Invalid record key"})

            # Get the customer's main record
            ref = db.reference(f"customers/{record_key}")
            record = ref.get()
            if not record:
                return JsonResponse({"success": False, "error": "Record not found"})

            current_date = datetime.today().strftime('%Y-%m-%d')  # Get today's date
            amc_due_date = record.get("amc_due_date", "")

            if not amc_due_date:
                return JsonResponse({"success": False, "error": "AMC Due Date not found"})

            # Prepare update data for customers collection
            update_data = {"remarks": remarks}
            if remarks == "Paid":
                if not bill_no or not utr_no:
                    return JsonResponse({"success": False, "error": "Bill number and UTR number are required when marking as Paid"})
                update_data.update({
                    "date_of_payment": current_date,
                    "bill_no": bill_no,
                    "utr_no": utr_no  # Store UTR number
                })

            # Update the customer's main record
            ref.update(update_data)

            # Reference to amc_status (where multiple records should exist)
            amc_status_ref = db.reference("amc_status")

            # Always create a new entry for the updated AMC status
            new_entry = amc_status_ref.push({
                "record_key": record_key,
                "amc_amount": record.get("amc_amount", ""),
                "amc_due_date": record.get("amc_due_date", ""),
                "party_cb": record.get("party_cb", ""),
                "branch_code": record.get("branch_code", ""), 
                "machine_serial_number": record.get("machine_serial_number", ""), 
                "machine_type": record.get("machine_type", ""), 
                "billing_address": record.get("billing_address", ""),
                "frequency": record.get("frequency", ""),
                "remarks": "Paid",
                "date_of_payment": current_date if remarks == "Paid" else "",
                "bill_no": bill_no if remarks == "Paid" else "",
                "utr_no": utr_no if remarks == "Paid" else ""  # Store UTR number
            })

            return JsonResponse({
                "success": True,
                "remarks": update_data.get("remarks"),
                "date_of_payment": update_data.get("date_of_payment", ""),
                "bill_no": update_data.get("bill_no", ""),
                "utr_no": update_data.get("utr_no", ""),
                "new_entry_key": new_entry.key  # Returning the new Firebase key for reference
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})














def pm_view(request):
    proforma_ref = db.reference('customers')

    # Fetch all Pro Forma data
    proforma_data = proforma_ref.get()

    # Define months for AMC fields
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]

    # Extract unique engineer names for the dropdown filter
    all_engineer_names = {str(data.get("engineer_name", "")).strip() for data in proforma_data.values() if "engineer_name" in data and data.get("engineer_name")} if proforma_data else set()
    
    # Get filter values from request
    selected_engineer = request.GET.get('engineer_name', 'all').strip().lower()
    selected_month = request.GET.get('month', 'all').strip()

    # Ensure data exists and filter only "Billed" Pro Forma invoices
    billed_proformas = []
    if proforma_data:
        for key, data in proforma_data.items():
            if data.get("status") == "Billed" and (selected_engineer == 'all' or str(data.get("engineer_name", "")).strip().lower() == selected_engineer):
                
                # Filter month-specific data
                month_values = {month: data.get(month, "0") for month in months}
                
                if selected_month != 'all':
                    month_value = data.get(selected_month)  # Get the value for the selected month
                    
                    if not month_value or month_value == "0":  # Skip if value is None or "0"
                        continue  # Exclude this row
                    
                    # Keep only the selected month field
                    month_values = {selected_month: month_value}

                
                billed_proformas.append({
                    "record_key": key,
                    "party_cb": data.get("party_cb", "N/A"),
                    "branch_code": data.get("branch_code", "N/A"),
                    "machine_serial_number": data.get("machine_serial_number", "N/A"),
                    "machine_type": data.get("machine_type", "N/A"),
                    "pi_date": data.get("pi_date", "N/A"),
                    "pi_no": data.get("pi_no", "N/A"),
                    "amc_due_date": data.get("amc_due_date", "N/A"),
                    "quantity": data.get("quantity", "N/A"),
                    "discount": data.get("discount", "N/A"),
                    "taxable_amt": data.get("taxable_amt", "N/A"),
                    "tax_amount": data.get("tax_amount", "N/A"),
                    "total_bill_amount": data.get("total_bill_amount", "N/A"),
                    "status": data.get("status", "N/A"),
                    "reference_by": data.get("reference_by", "N/A"),
                    "engineer_name": data.get("engineer_name", "N/A"),
                    **month_values  # Add filtered month data
                })

    return render(request, 'display_data/pm.html', {
        'data_list': billed_proformas,
        'all_engineer_names': sorted(all_engineer_names),
        'selected_engineer': selected_engineer,
        'months': months,  # Pass months list to the template
        'selected_month': selected_month
    })





@csrf_exempt
def update_pm(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            record_key = data.get("record_key")

            if not record_key:
                return JsonResponse({"error": "Missing record key"}, status=400)

            # Reference to the specific record in Firebase using the correct record key
            proforma_ref = db.reference(f'customers/{record_key}')

            # Ensure the record exists
            existing_data = proforma_ref.get()
            if not existing_data:
                return JsonResponse({"error": "Record not found"}, status=404)

            # Update Firebase record
            update_data = {
                "engineer_name": data.get("engineer_name", ""),
                "January": data.get("January", "0"),
                "February": data.get("February", "0"),
                "March": data.get("March", "0"),
                "April": data.get("April", "0"),
                "May": data.get("May", "0"),
                "June": data.get("June", "0"),
                "July": data.get("July", "0"),
                "August": data.get("August", "0"),
                "September": data.get("September", "0"),
                "October": data.get("October", "0"),
                "November": data.get("November", "0"),
                "December": data.get("December", "0"),
            }

            proforma_ref.update(update_data)

            # Fetch updated data to confirm changes
            updated_data = proforma_ref.get()

            return JsonResponse({"success": True, "message": "PM details updated successfully", "updated_data": updated_data})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)




import firebase_admin
from firebase_admin import credentials, db
from django.http import JsonResponse

def get_chart_data(request):
    # Reference to the "customers" node in Firebase
    customers_ref = db.reference('customers')
    
    # Fetch all customer data
    customers_data = customers_ref.get()
    
    if not customers_data:
        return JsonResponse({"error": "No data found"}, status=404)
    
    # Initialize dictionaries to store machine type counts and AMC amounts
    machine_counts = {}
    amc_amounts = {}
    
    for record_key, data in customers_data.items():
        machine_type = data.get("machine_type", "Unknown")
        
        try:
            amc_amount = float(data.get("amc_amount", 0))  # Ensure it's a float
        except ValueError:
            amc_amount = 0  # Handle cases where amc_amount is invalid
        
        # Update machine type counts
        machine_counts[machine_type] = machine_counts.get(machine_type, 0) + 1
        
        # Update AMC amounts
        amc_amounts[machine_type] = amc_amounts.get(machine_type, 0) + amc_amount
    
    return JsonResponse({"machine_counts": machine_counts, "amc_amounts": amc_amounts})
