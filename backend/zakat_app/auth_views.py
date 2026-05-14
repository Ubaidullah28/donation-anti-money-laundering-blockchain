from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import UserAccount, Charity, Donation, FundUnlockRequest
from .signature_verify import verify_signature
from .aml import check_aml
import hashlib
import uuid


# ====== AUTHENTICATION FORMS ======

class UserSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = UserAccount
        fields = ('username', 'email', 'password')

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
            raise forms.ValidationError("Passwords don't match!")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class CharitySignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    wallet_address = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Charity
        fields = ('name', 'wallet_address', 'description')

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
            raise forms.ValidationError("Passwords don't match!")

        wallet_address = cleaned_data.get('wallet_address')
        if wallet_address:
            wallet_address = wallet_address.strip().lower()
            if UserAccount.objects.filter(wallet_address__iexact=wallet_address).exists():
                raise forms.ValidationError("This wallet address is already registered with another account.")
            if Charity.objects.filter(wallet_address__iexact=wallet_address).exists():
                raise forms.ValidationError("This wallet address is already registered as a charity.")

        return cleaned_data

    def save(self, commit=True):
        # First create admin user
        admin_user = UserAccount.objects.create_user(
            username=f"charity_{self.cleaned_data.get('name').lower().replace(' ', '_')}",
            password=self.cleaned_data['password'],
            email=''
        )
        admin_user.wallet_address = self.cleaned_data.get('wallet_address')
        admin_user.wallet_verified = True
        admin_user.save()

        charity = super().save(commit=False)
        charity.admin_user = admin_user
        charity.verified = True
        if commit:
            charity.save()
        return charity


# ====== PUBLIC PAGES ======

def index(request):
    top_three_donations = Donation.objects.filter(verified=True).select_related('donor', 'charity').order_by('-amount')[:3]
    return render(request, "index.html", {
        "top_three_donations": top_three_donations
    })


def donation_history(request):
    filter_key = request.GET.get('filter', '')
    donations = Donation.objects.filter(verified=True).select_related('donor', 'charity')

    if filter_key == '50':
        donations = donations.filter(amount__gte=50)
    elif filter_key == '100':
        donations = donations.filter(amount__gte=100)
    elif filter_key == 'top3':
        donations = donations.order_by('-amount')[:3]
    else:
        donations = donations.order_by('-created_at')

    top_three_donations = Donation.objects.filter(verified=True).select_related('donor', 'charity').order_by('-amount')[:3]

    return render(request, "donation_history.html", {
        "donations": donations,
        "top_three_donations": top_three_donations,
        "selected_filter": filter_key,
    })


# ====== USER AUTHENTICATION ======

def user_signup(request):
    if request.user.is_authenticated:
        return redirect('donor_dashboard')

    if request.method == "POST":
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('donor_dashboard')
    else:
        form = UserSignUpForm()

    return render(request, "auth/user_signup.html", {"form": form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('donor_dashboard')

    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('donor_dashboard')
            else:
                form.add_error(None, "Invalid credentials")
    else:
        form = UserLoginForm()

    return render(request, "auth/user_login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect('index')


# ====== CHARITY AUTHENTICATION ======

def charity_signup(request):
    if request.user.is_authenticated and hasattr(request.user, 'charity_admin'):
        return redirect('charity_dashboard')

    if request.method == "POST":
        form = CharitySignUpForm(request.POST)
        if form.is_valid():
            wallet_address = form.cleaned_data.get('wallet_address')
            signature = request.POST.get('signature')
            message = request.POST.get('message')

            if not (wallet_address and signature and message and verify_signature(message, signature, wallet_address)):
                form.add_error('wallet_address', 'Wallet verification failed. Connect MetaMask and sign using the selected wallet.')
            else:
                charity = form.save()
                login(request, charity.admin_user)
                return redirect('charity_dashboard')
    else:
        form = CharitySignUpForm()

    return render(request, "auth/charity_signup.html", {"form": form})


def charity_login(request):
    if request.user.is_authenticated and hasattr(request.user, 'charity_admin'):
        return redirect('charity_dashboard')

    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user and hasattr(user, 'charity_admin'):
                login(request, user)
                return redirect('charity_dashboard')
            else:
                form.add_error(None, "Invalid credentials or not a charity account")
    else:
        form = UserLoginForm()

    return render(request, "auth/charity_login.html", {"form": form})


def charity_logout(request):
    logout(request)
    return redirect('index')


# ====== DONOR DASHBOARD ======

@login_required(login_url='user_login')
def donor_dashboard(request):
    user = request.user
    donations = Donation.objects.filter(donor=user).select_related('charity')
    fund_requests = FundUnlockRequest.objects.filter(donor=user).select_related('charity')

    return render(request, "donor/dashboard.html", {
        "donations": donations,
        "fund_requests": fund_requests,
        "total_donated": user.total_donated
    })


@login_required(login_url='user_login')
def donor_wallet(request):
    user = request.user
    return render(request, "donor/wallet.html", {"user": user})


@login_required(login_url='user_login')
def update_wallet(request):
    """MetaMask call to update wallet"""
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        wallet_address = data.get('wallet_address')
        signature = data.get('signature')
        message = data.get('message')

        if wallet_address and signature and message:
            if UserAccount.objects.filter(wallet_address__iexact=wallet_address).exclude(id=request.user.id).exists() or Charity.objects.filter(wallet_address__iexact=wallet_address).exists():
                return JsonResponse({"success": False, "message": "This wallet address is already registered with another account."})

            if verify_signature(message, signature, wallet_address):
                user = request.user
                user.wallet_address = wallet_address
                user.wallet_verified = True
                user.save()
                return JsonResponse({"success": True, "message": "Wallet verified!"})

    return JsonResponse({"success": False, "message": "Verification failed"})


@login_required(login_url='user_login')
def donate(request):
    charities = Charity.objects.filter(verified=True)

    if request.method == "POST":
        donor = request.user
        charity_id = request.POST.get('charity')
        amount = float(request.POST.get('amount'))
        reason = request.POST.get('reason', '')
        wallet_address = request.POST.get('wallet_address')
        signature = request.POST.get('signature')
        message = request.POST.get('message')

        try:
            charity = Charity.objects.get(id=charity_id)
        except Charity.DoesNotExist:
            return render(request, "success.html", {
                "flagged": True,
                "error": "Invalid charity selected."
            })

        # Verify MetaMask signature
        verified = False
        if wallet_address and signature and message and wallet_address == donor.wallet_address:
            verified = verify_signature(message, signature, wallet_address)

        if not verified:
            return render(request, "success.html", {
                "flagged": True,
                "error": "MetaMask signature verification failed. Ensure it's your verified wallet."
            })

        recent = Donation.objects.filter(charity=charity, donor=donor).values_list('donor', flat=True)
        flagged = check_aml(donor.username, amount, list(recent))

        # Generate stealth address (using hash for anonymity)
        stealth_hash = hashlib.sha256(
            (str(uuid.uuid4()) + wallet_address + str(donor.id)).encode()
        ).hexdigest()
        stealth_address = "0x" + stealth_hash[:40]

        donation = Donation.objects.create(
            donor=donor,
            charity=charity,
            wallet_address=wallet_address,
            stealth_address=stealth_address,
            amount=amount,
            reason=reason,
            flagged=flagged,
            signature=signature,
            message=message,
            verified=verified
        )

        donor.total_donated += amount
        donor.save()

        return render(request, "success.html", {
            "flagged": flagged,
            "verified": verified,
            "message": f"Successfully donated {amount} ETH to {charity.name}"
        })

    return render(request, "donor/donate.html", {"charities": charities})


@login_required(login_url='user_login')
def handle_fund_request(request, request_id):
    """Approve or reject fund unlock request"""
    try:
        fund_request = FundUnlockRequest.objects.get(id=request_id, donor=request.user)
    except FundUnlockRequest.DoesNotExist:
        return redirect('donor_dashboard')

    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'approve':
            fund_request.status = 'approved'
        elif action == 'reject':
            fund_request.status = 'rejected'
        fund_request.save()

    return redirect('donor_dashboard')


# ====== CHARITY DASHBOARD ======

@login_required(login_url='charity_login')
def charity_dashboard(request):
    user = request.user
    if not hasattr(user, 'charity_admin'):
        return redirect('charity_login')

    charity = user.charity_admin
    donations = Donation.objects.filter(charity=charity).select_related('donor')
    fund_requests = FundUnlockRequest.objects.filter(charity=charity).select_related('donor')

    return render(request, "charity/dashboard.html", {
        "charity": charity,
        "donations": donations,
        "fund_requests": fund_requests
    })


@login_required(login_url='charity_login')
def request_fund_unlock(request):
    user = request.user
    if not hasattr(user, 'charity_admin'):
        return redirect('charity_login')

    charity = user.charity_admin
    donations = Donation.objects.filter(charity=charity, verified=True, locked_balance__gt=0)

    if request.method == "POST":
        donation_id = request.POST.get('donation')
        amount = float(request.POST.get('amount'))
        reason = request.POST.get('reason')

        try:
            donation = Donation.objects.get(id=donation_id, charity=charity)
        except Donation.DoesNotExist:
            return render(request, "charity/request_fund.html", {
                "donations": donations,
                "error": "Invalid donation selected"
            })

        if amount <= 0:
            return render(request, "charity/request_fund.html", {
                "donations": donations,
                "error": "Request amount must be a positive number."
            })

        if amount > donation.locked_balance:
            return render(request, "charity/request_fund.html", {
                "donations": donations,
                "error": f"Request amount cannot exceed remaining locked balance ({donation.locked_balance} ETH)."
            })

        FundUnlockRequest.objects.create(
            charity=charity,
            donor=donation.donor,
            donation=donation,
            amount=amount,
            reason=reason
        )

        return render(request, "success.html", {
            "message": f"Fund unlock request sent to {donation.donor.username}"
        })

    return render(request, "charity/request_fund.html", {"donations": donations})
