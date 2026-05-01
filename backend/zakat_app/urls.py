from django.urls import include, path
from . import auth_views, views

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

    # Donor Dashboard & Features
    path('donor/dashboard/', auth_views.donor_dashboard, name='donor_dashboard'),
    path('donor/wallet/', auth_views.donor_wallet, name='donor_wallet'),
    path('donor/update-wallet/', auth_views.update_wallet, name='update_wallet'),
    path('donor/donate/', auth_views.donate, name='donate'),
    path('donor/fund-request/<int:request_id>/', auth_views.handle_fund_request, name='handle_fund_request'),

    # Charity Dashboard & Features
    path('charity/dashboard/', auth_views.charity_dashboard, name='charity_dashboard'),
    path('charity/request-fund/', auth_views.request_fund_unlock, name='request_fund_unlock'),

    # Legacy routes (compatibility)
    path('dashboard/', auth_views.donor_dashboard, name='dashboard'),
    path('donate/', auth_views.donate),
]
