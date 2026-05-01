from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Donation, Request, Charity
from .aml import check_aml
from .signature_verify import verify_signature

def donate(request):
    if request.method == "POST":
        donor = request.POST.get('donor')
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
        if wallet_address and signature and message:
            verified = verify_signature(message, signature, wallet_address)

        if not verified:
            return render(request, "success.html", {
                "flagged": True,
                "error": "MetaMask signature verification failed. Please ensure you signed the transaction."
            })

        recent = Donation.objects.filter(charity=charity).values_list('donor_name', flat=True)

        flagged = check_aml(donor, amount, list(recent))

        Donation.objects.create(
            donor_name=donor,
            charity=charity,
            wallet_address=wallet_address,
            amount=amount,
            reason=reason,
            flagged=flagged,
            signature=signature,
            message=message,
            verified=verified
        )

        return render(request, "success.html", {"flagged": flagged, "verified": verified})

    charities = Charity.objects.filter(verified=True)
    return render(request, "donate.html", {"charities": charities})


def index(request):
    return render(request, "index.html")

def dashboard(request):
    donations = Donation.objects.select_related('charity').all()
    requests = Request.objects.select_related('charity').all()
    return render(request, "dashboard.html", {"donations": donations, "requests": requests})





def create_request(request):
    if request.method == "POST":
        charity_id = request.POST.get('charity')
        purpose = request.POST.get('purpose')
        amount = float(request.POST.get('amount'))

        try:
            charity = Charity.objects.get(id=charity_id)
        except Charity.DoesNotExist:
            return render(request, "create_request.html", {
                "error": "Invalid charity selected.",
                "charities": Charity.objects.filter(verified=True)
            })

        Request.objects.create(
            charity=charity,
            purpose=purpose,
            amount=amount,
            recipient_wallet=charity.wallet_address
        )

        return redirect('/dashboard')

    charities = Charity.objects.filter(verified=True)
    return render(request, "create_request.html", {"charities": charities})




def approve_request(request, id):
    try:
        r = Request.objects.get(id=id)
        r.approvals += 1
        r.save()
    except Request.DoesNotExist:
        pass
    return redirect('/dashboard')


def execute_request(request, id):
    try:
        r = Request.objects.get(id=id)
        if r.approvals >= 2 and r.authority_approved:
            r.completed = True
            r.save()
    except Request.DoesNotExist:
        pass
    return redirect('/dashboard')


def approve_authority(request, id):
    """Authority approval for fund requests"""
    try:
        r = Request.objects.get(id=id)
        r.authority_approved = True
        r.save()
    except Request.DoesNotExist:
        pass
    return redirect('/dashboard')