from django.urls import path
from .views import get_firebase_data, download_csv
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sales/', views.sales_page, name='sales_page'),
    path('insight_management_solutions/', views.get_firebase_data, name='insight_management_solutions'),
    path('download_csv/', download_csv, name='download_csv'),
    path('add_data/', views.add_data, name='add_data'),
    path('upcoming_amc/', views.upcoming_amc, name='upcoming_amc'),
    path('edit_data/<str:record_key>/', views.edit_data, name='edit_data'),
    path('view_bill/<str:invoice_no>/', views.view_bill, name='view_bill'),
    path('user-complaints/', views.user_complaints, name='user_complaints'),
    path('product-details/', views.product_details, name='product_details'),
    path("add_product/", views.add_product, name="add_product"),
    path('view_complaint_details/', views.view_complaint_details, name='view_complaint_details'),
    path('agreement_form/', views.agreement_form, name='agreement_form'),
    path('agreement/', views.agreement, name='agreement'),
    path('proforma-invoice/', views.proforma_invoice, name='proforma_invoice'),
    path('update_status/', views.update_status, name='update_status'),
    path('sale/', views.sale_page, name='sale'),
    path('pm/', views.pm_view, name='pm_view'),
    path('update_pm/', views.update_pm, name='update_pm'),
    path('update_amc_details/', views.update_amc_details, name='update_amc_details'),
    path('amc/', views.amc_details, name='amc_details'),
    path('update-remarks/', views.update_amc_remarks, name='update_amc_remarks'),
    path('amc-status/', views.amc_status, name='amc_status'), 
    path("update_amc_status/", views.update_amc_status, name="update_amc_status"),
    path('get_chart_data/', views.get_chart_data, name='get_chart_data'),
]
