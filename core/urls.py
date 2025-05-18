from django.urls import path
from . import views

urlpatterns = [
    # Dashboard and staff account
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('accounts/create/', views.create_staff_account, name='create_staff'),

    # Drug management
    path('drugs/', views.drug_list, name='drug_list'),
    path('drugs/add/', views.drug_add, name='drug_add'),
    path('drugs/edit/<int:pk>/', views.drug_edit, name='drug_edit'),
    path('drugs/delete/<int:pk>/', views.drug_delete, name='drug_delete'),

    # Sales management
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/add/', views.sale_add, name='sale_add'),
    path('sales/summary/', views.sales_summary, name='sales_summary'),

    # Reports
    path('reports/profit/', views.profit_report, name='profit_report'),
    path('sales/export/pdf/', views.export_sales_pdf, name='export_sales_pdf'),
    path('sales/pdf/', views.export_sales_pdf, name='sales_pdf'),
    path('profit/pdf/', views.export_profit_pdf, name='profit_pdf'),

    #debtors
    path('debtors/', views.debtor_list, name='debtor_list'),
    path('debtors/add/', views.debtor_add, name='debtor_add'),

    # urls.py
    path('about/', views.about_view, name='about'),
]
