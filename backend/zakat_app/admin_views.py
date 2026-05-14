from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from .models import UserAccount, Charity, Donation, Admin, FundUnlockRequest, CharityExpense
from cryptography.fernet import Fernet

ENCRYPTION_KEY = b'abcdefghijklmnopqrstuvwxzy12345678901234567890123456789012'

# ====== ADMIN AUTHENTICATION ======

@never_cache
def admin_login(request):
    """Admin login page"""
    if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
        return redirect('admin_dashboard')

    error_message = None
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            error_message = "Both username and password are required."
        else:
            user = authenticate(username=username, password=password)
            if user and Admin.objects.filter(user=user).exists():
                login(request, user)
                return redirect('admin_dashboard')
            error_message = "Invalid credentials or not an admin account"

    return render(request, "admin/login.html", {
        "error": error_message
    } if error_message else {})


def admin_logout(request):
    """Admin logout"""
    logout(request)
    return redirect('index')


# ====== ADMIN DASHBOARD ======

@login_required(login_url='admin_login')
@never_cache
def admin_dashboard(request):
    """Main admin dashboard"""
    # Check if user is admin
    if not Admin.objects.filter(user=request.user).exists():
        return redirect('admin_login')

    total_donations = Donation.objects.count()
    total_donors = UserAccount.objects.filter(donations__isnull=False).distinct().count()
    total_charities = Charity.objects.count()
    flagged_donations = Donation.objects.filter(flagged=True).count()
    all_admins = Admin.objects.select_related('user').all()

    context = {
        'total_donations': total_donations,
        'total_donors': total_donors,
        'total_charities': total_charities,
        'flagged_donations': flagged_donations,
        'all_admins': all_admins,
    }

    return render(request, "admin/dashboard.html", context)


@login_required(login_url='admin_login')
@never_cache
def view_donors(request):
    """View all donors with their KYC info decrypted"""
    if not Admin.objects.filter(user=request.user).exists():
        return redirect('admin_login')

    donors = UserAccount.objects.exclude(donations__isnull=True).distinct()
    donors_data = []

    for donor in donors:
        try:
            kyc_info = donor.decrypt_kyc() if donor.encrypted_kyc else "No KYC"
        except:
            kyc_info = "Decryption Error"

        donors_data.append({
            'id': donor.id,
            'username': donor.username,
            'email': donor.email,
            'wallet_address': donor.wallet_address,
            'kyc_decrypted': kyc_info,
            'total_donated': donor.total_donated,
            'created_at': donor.created_at,
        })

    return render(request, "admin/view_donors.html", {'donors': donors_data})


@login_required(login_url='admin_login')
@never_cache
def view_donor_details(request, donor_id):
    """View detailed KYC info for a specific donor"""
    if not Admin.objects.filter(user=request.user).exists():
        return redirect('admin_login')

    try:
        donor = UserAccount.objects.get(id=donor_id)
    except UserAccount.DoesNotExist:
        return render(request, "admin/error.html", {"message": "Donor not found"})

    try:
        kyc_decrypted = donor.decrypt_kyc() if donor.encrypted_kyc else "No KYC"
    except:
        kyc_decrypted = "Decryption Error"

    donations = Donation.objects.filter(donor=donor).select_related('charity').order_by('-created_at')

    context = {
        'donor': donor,
        'kyc_decrypted': kyc_decrypted,
        'donations': donations,
    }

    return render(request, "admin/donor_details.html", context)


@login_required(login_url='admin_login')
@never_cache
def view_donations(request):
    """View all donations with public address only"""
    if not Admin.objects.filter(user=request.user).exists():
        return redirect('admin_login')

    donations = Donation.objects.select_related('donor', 'charity').order_by('-created_at')

    context = {
        'donations': donations,
    }

    return render(request, "admin/view_donations.html", context)


@login_required(login_url='admin_login')
@never_cache
def view_charities(request):
    """View all charities"""
    if not Admin.objects.filter(user=request.user).exists():
        return redirect('admin_login')

    charities = Charity.objects.all()

    context = {
        'charities': charities,
    }

    return render(request, "admin/view_charities.html", context)


@login_required(login_url='admin_login')
@never_cache
def view_charity_expenses(request):
    """View all charity expenses"""
    if not Admin.objects.filter(user=request.user).exists():
        return redirect('admin_login')

    expenses = CharityExpense.objects.select_related('charity').order_by('-created_at')
    pending_expenses = expenses.filter(approved_by_admin=False).count()
    approved_total = sum(exp.amount for exp in expenses if exp.approved_by_admin)

    context = {
        'expenses': expenses,
        'pending_expenses': pending_expenses,
        'approved_total': approved_total,
    }

    return render(request, "admin/view_charity_expenses.html", context)


@login_required(login_url='admin_login')
@never_cache
def approve_expense(request, expense_id):
    """Approve a charity expense"""
    if not Admin.objects.filter(user=request.user).exists():
        return redirect('admin_login')

    try:
        expense = CharityExpense.objects.get(id=expense_id)
        expense.approved_by_admin = True
        expense.save()
        return redirect('view_charity_expenses')
    except CharityExpense.DoesNotExist:
        return render(request, "admin/error.html", {"message": "Expense not found"})


@login_required(login_url='admin_login')
@never_cache
def flag_donation(request, donation_id):
    """Flag a donation for review"""
    if not Admin.objects.filter(user=request.user).exists():
        return redirect('admin_login')

    try:
        donation = Donation.objects.get(id=donation_id)
        donation.flagged = not donation.flagged
        donation.save()
        return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))
    except Donation.DoesNotExist:
        return render(request, "admin/error.html", {"message": "Donation not found"})


@login_required(login_url='admin_login')
@never_cache
def register_admin(request):
    """Register a new admin (only existing admins can do this)"""
    if not Admin.objects.filter(user=request.user).exists():
        return redirect('admin_login')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        email = request.POST.get('email', '')

        if password != password_confirm:
            return render(request, "admin/register_admin.html", {
                "error": "Passwords don't match!"
            })

        if UserAccount.objects.filter(username=username).exists():
            return render(request, "admin/register_admin.html", {
                "error": "Username already exists!"
            })

        # Create new admin user
        new_user = UserAccount.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create Admin record
        Admin.objects.create(user=new_user, can_decrypt=True)

        return render(request, "admin/register_admin.html", {
            "success": f"Admin '{username}' registered successfully!"
        })

    return render(request, "admin/register_admin.html")


@login_required(login_url='admin_login')
def search_donor(request):
    """Search for a donor by name or wallet"""
    if not Admin.objects.filter(user=request.user).exists():
        return redirect('admin_login')

    query = request.GET.get('q', '')
    donors = []

    if query:
        donors = UserAccount.objects.filter(
            username__icontains=query
        ) | UserAccount.objects.filter(
            wallet_address__icontains=query
        )

    context = {
        'query': query,
        'donors': donors,
    }

    return render(request, "admin/search_donor.html", context)
