from django.urls import include, path
from . import auth_views, views, admin_views

urlpatterns = [
    # Public
    path('', auth_views.index, name='index'),

    # User Authentication
    path('user/signup/', auth_views.user_signup, name='user_signup'),
    path('user/login/', auth_views.user_login, name='user_login'),
    path('user/logout/', auth_views.user_logout, name='user_logout'),

    # Charity Authentication
    path('charity/signup/', auth_views.charity_signup, name='charity_signup'),
    path('charity/login/', auth_views.charity_login, name='charity_login'),
    path('charity/logout/', auth_views.charity_logout, name='charity_logout'),
    path('history/', auth_views.donation_history, name='donation_history'),

    # Donor Dashboard & Features
    path('donor/dashboard/', auth_views.donor_dashboard, name='donor_dashboard'),
    path('donor/wallet/', auth_views.donor_wallet, name='donor_wallet'),
    path('donor/update-wallet/', auth_views.update_wallet, name='update_wallet'),
    path('donor/donate/', auth_views.donate, name='donate'),
    path('donor/fund-request/<int:request_id>/', auth_views.handle_fund_request, name='handle_fund_request'),

    # Charity Dashboard & Features
    path('charity/dashboard/', auth_views.charity_dashboard, name='charity_dashboard'),
    path('charity/request-fund/', auth_views.request_fund_unlock, name='request_fund_unlock'),
    path('charity/submit-expense/', auth_views.submit_expense, name='submit_expense'),

    # Admin Panel
    path('admin/login/', admin_views.admin_login, name='admin_login'),
    path('admin/logout/', admin_views.admin_logout, name='admin_logout'),
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/donors/', admin_views.view_donors, name='admin_view_donors'),
    path('admin/donor/<int:donor_id>/', admin_views.view_donor_details, name='admin_donor_details'),
    path('admin/donations/', admin_views.view_donations, name='admin_view_donations'),
    path('admin/charities/', admin_views.view_charities, name='admin_view_charities'),
    path('admin/charity-expenses/', admin_views.view_charity_expenses, name='view_charity_expenses'),
    path('admin/approve-expense/<int:expense_id>/', admin_views.approve_expense, name='approve_expense'),
    path('admin/flag/<int:donation_id>/', admin_views.flag_donation, name='admin_flag_donation'),
    path('admin/register-admin/', admin_views.register_admin, name='admin_register_admin'),
    path('admin/search-donor/', admin_views.search_donor, name='admin_search_donor'),

    # Legacy routes (compatibility)
    path('dashboard/', auth_views.donor_dashboard, name='dashboard'),
    path('donate/', auth_views.donate),
]
