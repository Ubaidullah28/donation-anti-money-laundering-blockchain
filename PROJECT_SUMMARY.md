# Blockchain-Based Transparent Zakat Distribution System
## Comprehensive Project Summary Report

---

## 1. PROJECT OVERVIEW

### 1.1 Purpose
A **transparent and traceable zakat distribution & anti-Money Laudering checks system** leveraging blockchain technology with built-in Anti-Money Laundering (AML) checks. The system enables:
- **Secure donations** from donors to verified charity organizations
- **Transparent tracking** of all transactions on blockchain
- **Fraud prevention** through AML compliance checks
- **MetaMask wallet integration** for cryptographic verification
- **Dual-role authentication** (Donors & Charity Organizations)

### 1.2 Core Problem Statement
Traditional donation systems lack transparency and traceability. This project addresses:
- Lack of accountability in fund distribution
- Inability to track where donations go
- High risk of money laundering
- Limited fraud detection mechanisms
- Trust issues between donors and organizations

### 1.3 Key Innovation
Uses **Ethereum message signing** (MetaMask) to cryptographically verify both donor and charity identities without requiring centralized private keys or complex wallet management.

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Django Templates)             │
│  ┌────────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │ Donor Pages    │    │ Charity Pages│    │ Home/Index   │   │
│  └────────────────┘    └──────────────┘    └──────────────┘   │
└──────────┬──────────────────────────┬──────────────────────────┘
           │                          │
      MetaMask API              Django Server
      Web3.js Library           Port 8000
           │                          │
┌──────────┴──────────────────────────┴──────────────────────────┐
│                      Django Backend (zakat_app)                │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Views (Auth, Donation, Fund Requests)                 │   │
│  │  - Authentication (Donor & Charity)                    │   │
│  │  - Donation Processing & Verification                 │   │
│  │  - Fund Unlock Request Management                      │   │
│  └────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Signature Verification (signature_verify.py)          │   │
│  │  - Uses Web3.py for Ethereum message recovery          │   │
│  │  - Validates MetaMask signatures                       │   │
│  └────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  AML Checks (aml.py)                                   │   │
│  │  - Transaction amount threshold (100,000)              │   │
│  │  - Frequency limit checks (5 donations per period)     │   │
│  └────────────────────────────────────────────────────────┘   │
└──────────┬──────────────────────────────────────────────────────┘
           │
┌──────────┴──────────────────────────────────────────────────────┐
│               Database (SQLite3 - db.sqlite3)                   │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ Tables:                                              │       │
│  │ - zakat_app_useraccount (Custom User Model)         │       │
│  │ - zakat_app_charity (Charity Organizations)          │       │
│  │ - zakat_app_donation (Donation Records)              │       │
│  │ - zakat_app_fundunlockrequest (Fund Requests)       │       │
│  │ - zakat_app_request (Legacy Fund Requests)           │       │
│  └──────────────────────────────────────────────────────┘       │
└───────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Breakdown
1. **Frontend**: Django templates with Web3.js for MetaMask integration
2. **Backend**: Django REST Framework + Custom Views
3. **Authentication**: MetaMask wallet signatures (secp256k1 cryptography)
4. **Database**: SQLite3 with custom user model
5. **Blockchain**: Ethereum message signing (Sepolia testnet compatible)

---

## 3. TECHNOLOGY STACK

### Backend
- **Framework**: Django 4.2
- **Database**: SQLite3
- **Authentication**: Custom AbstractUser model + MetaMask
- **Cryptography**: Web3.py, eth-account (Ethereum signature verification)
- **API**: Django REST Framework

### Frontend
- **Template Engine**: Django Templates (Jinja2)
- **JavaScript Library**: Web3.js (MetaMask communication)
- **Wallet Integration**: MetaMask browser extension
- **Styling**: CSS (Bootstrap-like)

### Blockchain
- **Network**: Ethereum (Sepolia testnet)
- **Signing Method**: Personal_sign (EIP-191)
- **Smart Contract**: Solidity (Zakat.sol)

### Dependencies
```
Django==4.2
djangorestframework
web3==6.0.0
eth-account
eth-keys
eth-utils
```

---

## 4. DATABASE SCHEMA

### 4.1 Entity-Relationship Diagram

```
UserAccount (Custom User Model)
├── id (PK)
├── username (unique)
├── email
├── password (hashed)
├── wallet_address (unique, nullable)
├── wallet_verified (boolean)
├── total_donated (float)
├── created_at (timestamp)
└── is_staff, is_superuser (Django defaults)

    ↓ (OneToOne)
    
Charity
├── id (PK)
├── name
├── admin_user (FK → UserAccount)
├── wallet_address (unique)
├── description
├── verified (boolean)
└── created_at (timestamp)

    ↓
    
Donation
├── id (PK)
├── donor (FK → UserAccount)
├── charity (FK → Charity)
├── wallet_address
├── amount (float - in ETH)
├── reason (text)
├── flagged (boolean - AML flag)
├── signature (text - MetaMask signature)
├── message (text - signed message)
├── verified (boolean)
└── created_at (timestamp)

    ↓
    
FundUnlockRequest
├── id (PK)
├── charity (FK → Charity)
├── donor (FK → UserAccount)
├── donation (FK → Donation)
├── amount (float)
├── reason (text)
├── status (choices: pending, approved, rejected)
├── created_at (timestamp)
└── updated_at (timestamp)
```

### 4.2 Model Code

```python
class UserAccount(AbstractUser):
    """Extended User model for donors"""
    wallet_address = models.CharField(max_length=200, blank=True, null=True)
    wallet_verified = models.BooleanField(default=False)
    total_donated = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class Charity(models.Model):
    """Charity organization account"""
    name = models.CharField(max_length=200)
    admin_user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, 
                                      related_name='charity_admin')
    wallet_address = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Donation(models.Model):
    """Donation records with blockchain verification"""
    donor = models.ForeignKey(UserAccount, on_delete=models.CASCADE, 
                            related_name='donations')
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, 
                               related_name='donations')
    wallet_address = models.CharField(max_length=200, blank=True, null=True)
    amount = models.FloatField()
    reason = models.TextField(blank=True)
    flagged = models.BooleanField(default=False)  # AML flag
    signature = models.TextField(blank=True, null=True)  # MetaMask signature
    message = models.TextField(blank=True, null=True)  # Signed message
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class FundUnlockRequest(models.Model):
    """Charity requests to unlock donated funds"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, 
                               related_name='fund_requests')
    donor = models.ForeignKey(UserAccount, on_delete=models.CASCADE, 
                            related_name='fund_requests_received')
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    amount = models.FloatField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, 
                            default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

## 5. AUTHENTICATION SYSTEM

### 5.1 Dual-Role Authentication Architecture

#### Donor Authentication Flow
```
1. User Signs Up (Donor)
   └─ Username, Email, Password
   └─ Wallet: Initially empty (verified=False)
   
2. User Logs In
   └─ Username + Password
   └─ Session created
   
3. User Verifies Wallet
   └─ Clicks "Verify Wallet" on donor dashboard
   └─ MetaMask popup for account selection
   └─ Signs message: "Verify wallet 0x..."
   └─ Backend verifies signature with verify_signature()
   └─ wallet_verified = True
   └─ wallet_address stored
```

#### Charity Authentication Flow
```
1. Organization Signs Up (Charity)
   └─ Organization Name + Description
   └─ Wallet Address (from MetaMask)
   └─ Message to sign: "Register charity {name} with address {wallet}"
   └─ Password for login
   
2. On Form Submit
   └─ MetaMask signature verification required
   └─ Signature must match wallet_address
   └─ If verified → Charity created with verified=True
   └─ charity_username auto-generated as: charity_{organization_name}
   
3. Charity Logs In
   └─ Username (charity_xxxx) + Password
   └─ Access to charity dashboard
   └─ Can view donations received
   └─ Can request fund unlocks
```

### 5.2 Key Authentication Code

#### Signature Verification (using eth-account)
```python
from web3 import Web3
from eth_account.messages import encode_defunct

def verify_signature(message, signature, wallet_address):
    """
    Verify Ethereum message signature
    Uses EIP-191 standard for message hashing
    """
    try:
        w3 = Web3()
        # Encode message as per Ethereum standard
        message_hash = encode_defunct(text=message)
        # Recover wallet address from signature
        recovered_address = w3.eth.account.recover_message(
            message_hash, 
            signature=signature
        )
        # Compare addresses (case-insensitive)
        return recovered_address.lower() == wallet_address.lower()
    except Exception as e:
        print(f"Verification error: {str(e)}")
        return False
```

#### Donor Wallet Verification View
```python
@login_required(login_url='user_login')
def update_wallet(request):
    """MetaMask wallet verification endpoint"""
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        wallet_address = data.get('wallet_address')
        signature = data.get('signature')
        message = data.get('message')

        # Check wallet isn't already registered
        if UserAccount.objects.filter(
            wallet_address__iexact=wallet_address
        ).exclude(id=request.user.id).exists():
            return JsonResponse({
                "success": False, 
                "message": "Wallet already registered"
            })

        if wallet_address and signature and message:
            if verify_signature(message, signature, wallet_address):
                user = request.user
                user.wallet_address = wallet_address
                user.wallet_verified = True
                user.save()
                return JsonResponse({
                    "success": True, 
                    "message": "Wallet verified!"
                })

    return JsonResponse({"success": False})
```

#### Charity Signup Form
```python
class CharitySignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(
        widget=forms.PasswordInput, 
        label="Confirm Password"
    )
    wallet_address = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

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
            # Ensure wallet uniqueness across all users
            if UserAccount.objects.filter(
                wallet_address__iexact=wallet_address
            ).exists():
                raise forms.ValidationError(
                    "Wallet already registered with donor account"
                )
            if Charity.objects.filter(
                wallet_address__iexact=wallet_address
            ).exists():
                raise forms.ValidationError(
                    "Charity with this wallet already exists"
                )
        return cleaned_data

    def save(self, commit=True):
        # Create admin user for charity
        admin_user = UserAccount.objects.create_user(
            username=f"charity_{self.cleaned_data.get('name').lower().replace(' ', '_')}",
            password=self.cleaned_data['password'],
            email=''
        )
        admin_user.wallet_address = self.cleaned_data.get('wallet_address')
        admin_user.wallet_verified = True
        admin_user.save()

        # Create and link charity
        charity = super().save(commit=False)
        charity.admin_user = admin_user
        charity.verified = True  # Auto-verified via MetaMask
        if commit:
            charity.save()
        return charity
```

---

## 6. METAMASK INTEGRATION

### 6.1 Frontend MetaMask Implementation

#### Charity Signup with MetaMask (JavaScript)
```javascript
async function connectMetaMask() {
    if (!window.ethereum) {
        alert('MetaMask is not installed.');
        return null;
    }
    try {
        const accounts = await window.ethereum.request({ 
            method: 'eth_requestAccounts' 
        });
        return handleAccountsChanged(accounts);
    } catch (error) {
        alert('MetaMask connection failed: ' + error.message);
        return null;
    }
}

function handleAccountsChanged(accounts) {
    if (!accounts || accounts.length === 0) {
        walletHint.textContent = 'No MetaMask account selected';
        walletInput.value = '';
        return null;
    }
    const account = accounts[0];
    walletInput.value = account;
    walletHint.textContent = `Connected wallet: ${account}`;
    return account;
}

async function signSignupMessage(account) {
    const orgName = document.querySelector('[name="name"]').value.trim() || 'charity';
    const message = `Register charity ${orgName} with MetaMask address ${account}`;
    try {
        const signature = await window.ethereum.request({
            method: 'personal_sign',
            params: [message, account]
        });
        signatureInput.value = signature;
        messageInput.value = message;
        return true;
    } catch (error) {
        alert('Wallet signature declined: ' + error.message);
        return false;
    }
}

// Listen for account changes
window.ethereum.on('accountsChanged', handleAccountsChanged);
```

#### Donor Donation Process (JavaScript)
```javascript
async function submitDonation() {
    if (!walletVerified) {
        alert('Please verify your wallet first!');
        return;
    }

    const charity_select = document.querySelector('[name="charity"]');
    const amount = document.querySelector('[name="amount"]').value.trim();
    const reason = document.querySelector('[name="reason"]').value.trim();

    if (!charity_select.value || !amount) {
        alert('Please fill in all required fields');
        return;
    }

    // Connect MetaMask and get account
    const account = await connectAndSelectAccount();
    if (!account) return;

    // Verify it matches their registered wallet
    if (account.toLowerCase() !== userWallet.toLowerCase()) {
        alert(`Account mismatch!\nRegistered: ${userWallet}\nSelected: ${account}`);
        return;
    }

    // Sign the donation message
    web3 = new Web3(window.ethereum);
    const charityName = charity_select.options[charity_select.selectedIndex].text;
    const message = `Donate ${amount} ETH to ${charityName}. Reason: ${reason}`;

    try {
        const signature = await web3.eth.personal.sign(message, account, '');
        
        // Populate form with signature details
        document.getElementById('wallet_address').value = account;
        document.getElementById('message').value = message;
        document.getElementById('signature').value = signature;
        
        // Submit form to backend for verification
        document.getElementById('donationForm').submit();
    } catch (error) {
        alert('Signature failed: ' + error.message);
    }
}

async function switchMetaMaskAccount() {
    if (!window.ethereum) {
        alert('MetaMask not installed!');
        return;
    }
    try {
        const accounts = await window.ethereum.request({
            method: 'eth_requestAccounts'
        });
        if (accounts && accounts.length > 0) {
            const selectedAccount = accounts[0];
            if (selectedAccount.toLowerCase() === userWallet.toLowerCase()) {
                alert(`✓ Correct account!\n${selectedAccount}`);
            } else {
                alert(`Account: ${selectedAccount}\nRegistered: ${userWallet}`);
            }
        }
    } catch (error) {
        alert('Account selection failed: ' + error.message);
    }
}
```

### 6.2 Key MetaMask Methods Used
- `eth_requestAccounts` - Request wallet access
- `personal_sign` - Sign message with private key (EIP-191)
- `eth_accounts` - Get currently connected accounts
- `accountsChanged` - Event listener for account switches

---

## 7. DONATION FLOW

### 7.1 Complete Donation Process

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DONOR INITIATES DONATION                                │
│    └─ Navigates to /donor/donate/                          │
│    └─ Page shows: Registered wallet, verified status       │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 2. FILL DONATION FORM                                      │
│    └─ Select charity organization (verified charities only)│
│    └─ Enter amount (in ETH)                                │
│    └─ Enter reason (optional)                              │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 3. CLICK "SWITCH METAMASK ACCOUNT" (if needed)            │
│    └─ Prompts user to select correct MetaMask account      │
│    └─ Verifies if account matches registered wallet        │
│    └─ Shows confirmation or warning                        │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 4. SIGN WITH METAMASK                                     │
│    └─ Click "Sign & Donate with MetaMask"                 │
│    └─ Frontend calls connectAndSelectAccount()            │
│    └─ Verifies account matches registered wallet          │
│    └─ Creates message: "Donate X ETH to {charity}"        │
│    └─ web3.eth.personal.sign(message, account)            │
│    └─ User confirms in MetaMask popup                      │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 5. SUBMIT TO BACKEND                                       │
│    └─ POST /donor/donate/                                  │
│    └─ Data: charity, amount, reason, wallet_address,      │
│          signature, message                                │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 6. BACKEND VERIFICATION                                    │
│    └─ Retrieve charity object                              │
│    └─ Call verify_signature(message, signature,            │
│        wallet_address)                                     │
│    └─ If failed: Return error page                         │
│    └─ If success: Continue to AML check                    │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 7. AML CHECKS                                              │
│    └─ call check_aml(donor.username, amount,              │
│        recent_transactions)                                │
│    └─ Check: amount <= 100,000 ETH?                       │
│    └─ Check: frequency <= 5 donations?                     │
│    └─ Return: flagged=True/False                           │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 8. CREATE DONATION RECORD                                   │
│    └─ Donation.objects.create(                             │
│        donor=donor,                                        │
│        charity=charity,                                    │
│        amount=amount,                                      │
│        wallet_address=wallet,                              │
│        message=message,                                    │
│        signature=signature,                                │
│        flagged=flagged,                                    │
│        verified=True                                       │
│    )                                                        │
│    └─ Update donor.total_donated += amount                 │
│    └─ Update donor.save()                                  │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 9. SUCCESS RESPONSE                                         │
│    └─ Render success.html page                             │
│    └─ Show: donation amount, charity name                  │
│    └─ Show: verified status, flagged status (if any)       │
│    └─ Option to view dashboard or make another donation    │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Donation Backend Code

```python
@login_required(login_url='user_login')
def donate(request):
    """Main donation endpoint"""
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

        # STEP 1: Verify MetaMask signature
        verified = False
        if wallet_address and signature and message:
            # Ensure it's their registered wallet
            if wallet_address == donor.wallet_address:
                verified = verify_signature(message, signature, wallet_address)

        if not verified:
            return render(request, "success.html", {
                "flagged": True,
                "error": "MetaMask signature verification failed."
            })

        # STEP 2: AML Check
        recent = Donation.objects.filter(
            charity=charity, 
            donor=donor
        ).values_list('donor', flat=True)
        flagged = check_aml(donor.username, amount, list(recent))

        # STEP 3: Create Donation Record
        donation = Donation.objects.create(
            donor=donor,
            charity=charity,
            wallet_address=wallet_address,
            amount=amount,
            reason=reason,
            flagged=flagged,
            signature=signature,
            message=message,
            verified=verified
        )

        # STEP 4: Update donor total
        donor.total_donated += amount
        donor.save()

        # STEP 5: Return success
        return render(request, "success.html", {
            "flagged": flagged,
            "verified": verified,
            "message": f"Successfully donated {amount} ETH to {charity.name}"
        })

    return render(request, "donor/donate.html", {"charities": charities})
```

---

## 8. ANTI-MONEY LAUNDERING (AML) SYSTEM

### 8.1 AML Thresholds and Logic

```python
THRESHOLD = 100000  # Maximum amount per transaction
FREQUENCY_LIMIT = 5  # Maximum donations in a period

def check_aml(donor, amount, recent_transactions):
    """
    AML violation checks:
    1. Amount exceeds threshold → Flag
    2. Donor exceeds frequency limit → Flag
    """
    # Check amount
    if amount > THRESHOLD:
        return True  # Flagged
    
    # Check frequency
    if recent_transactions.count(donor) > FREQUENCY_LIMIT:
        return True  # Flagged
    
    return False  # Not flagged
```

### 8.2 Risk Categories

| Risk Level | Condition | Action |
|-----------|-----------|--------|
| **LOW** | Amount < 100K, Frequency < 5 | Process immediately |
| **MEDIUM** | Amount > 100K | Flag for review |
| **MEDIUM** | Frequency > 5 | Flag for review |
| **HIGH** | Multiple violations | Require authority approval |

### 8.3 AML Integration in Donation Flow

- Every donation triggers `check_aml()` before creation
- Flagged donations stored with `flagged=True` in database
- Flagged donations still processed but marked for review
- Admin can view flagged donations in Django admin panel

---

## 9. FUND UNLOCK REQUEST SYSTEM

### 9.1 Purpose
Allows charities to request approval from donors to actually use (unlock) the donated funds after verification period.

### 9.2 Fund Request Workflow

```
┌─────────────────────────────────────────────┐
│ 1. DONATION MADE & VERIFIED                 │
│    └─ Funds locked initially                │
│    └─ Stored in donation record            │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ 2. CHARITY REQUESTS UNLOCK                  │
│    └─ Charity Dashboard → Create Request    │
│    └─ Select donation to unlock             │
│    └─ Specify amount & reason               │
│    └─ Submit request                        │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ 3. REQUEST CREATED                          │
│    └─ Status: "pending"                     │
│    └─ AML approval check                    │
│    └─ Notify donor                          │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ 4. DONOR REVIEWS IN THEIR DASHBOARD         │
│    └─ Fund Unlock Requests section          │
│    └─ View: Charity, Amount, Reason         │
└────────────────┬────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼─────────┐   ┌──▼──────────────┐
│ 5a. APPROVE     │   │ 5b. REJECT      │
│    └ Status:    │   │    └ Status:    │
│      approved   │   │      rejected    │
│    └ Funds sent │   │    └ Funds stay │
└─────────────────┘   │      locked     │
                      └─────────────────┘
```

### 9.3 Fund Request Model & Views

```python
class FundUnlockRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    donor = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    amount = models.FloatField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, 
                            default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Handler view for donor approval/rejection
@login_required(login_url='user_login')
def handle_fund_request(request, request_id):
    """Approve or reject fund unlock request"""
    try:
        fund_request = FundUnlockRequest.objects.get(
            id=request_id, 
            donor=request.user
        )
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
```

---

## 10. FRONTEND PAGES

### 10.1 Page Structure

```
/frontend/templates/
├── base.html                          # Base template with navigation
├── index.html                         # Home page
├── success.html                       # Donation success page
├── auth/
│   ├── user_login.html               # Donor login
│   ├── user_signup.html              # Donor registration
│   ├── charity_login.html            # Charity login
│   └── charity_signup.html           # Charity registration (with MetaMask)
├── donor/
│   ├── dashboard.html                # Donor dashboard
│   ├── donate.html                   # Donation form with MetaMask
│   └── wallet.html                   # Wallet verification page
└── charity/
    └── dashboard.html                # Charity dashboard
```

### 10.2 Key Pages

#### base.html - Navigation
```html
<nav>
    <a href="/">Home</a>
    <a href="/dashboard">Dashboard</a>
    <a href="/wallet">Wallet</a>
    <a href="/donate">Donate</a>
    <a href="/logout">Logout</a>
</nav>
```

#### index.html - Home Page
- Project description
- Key features list
- Call-to-action buttons
- Quick links to login/signup

#### donor/donate.html - Main Donation Interface
- Current wallet display + verification status
- Charity selection dropdown (only verified charities)
- Amount input
- Donation reason textarea
- MetaMask signature buttons:
  - "Switch MetaMask Account" (with account verification)
  - "Sign & Donate with MetaMask" (actual donation)

#### auth/charity_signup.html - Charity Registration
- Organization name input
- "Connect MetaMask" button
- Wallet address (auto-filled, read-only from MetaMask)
- Organization description
- Password fields
- Message displayed for signature confirmation

#### donor/wallet.html - Wallet Verification
- Display current wallet status
- "Connect & Verify Wallet" button
- Sign message process
- Wallet verification history

---

## 11. BACKEND VIEWS & ENDPOINTS

### 11.1 URL Routes

```python
# Authentication URLs
path('user/signup/', user_signup, name='user_signup')
path('user/login/', user_login, name='user_login')
path('user/logout/', user_logout, name='user_logout')

path('charity/signup/', charity_signup, name='charity_signup')
path('charity/login/', charity_login, name='charity_login')
path('charity/logout/', charity_logout, name='charity_logout')

# Main Pages
path('', index, name='index')

# Donor Routes
path('donor/dashboard/', donor_dashboard, name='donor_dashboard')
path('donor/wallet/', donor_wallet, name='donor_wallet')
path('donor/donate/', donate, name='donate')

# Charity Routes
path('charity/dashboard/', charity_dashboard, name='charity_dashboard')

# API Endpoints
path('api/update-wallet/', update_wallet, name='update_wallet')
path('handle-fund-request/<int:request_id>/', handle_fund_request, 
     name='handle_fund_request')
```

### 11.2 Main View Functions

```python
# DONOR VIEWS

def donor_dashboard(request):
    """Donor dashboard showing donations & fund requests"""
    user = request.user
    donations = Donation.objects.filter(donor=user)
    fund_requests = FundUnlockRequest.objects.filter(donor=user)
    return render(request, "donor/dashboard.html", {
        "donations": donations,
        "fund_requests": fund_requests,
        "total_donated": user.total_donated
    })

def donor_wallet(request):
    """Wallet verification page"""
    return render(request, "donor/wallet.html", {"user": request.user})

def update_wallet(request):
    """API endpoint for wallet update via AJAX"""
    if request.method == "POST":
        data = json.loads(request.body)
        wallet, sig, msg = data.get('wallet_address'), data.get('signature'), data.get('message')
        
        if verify_signature(msg, sig, wallet):
            user = request.user
            user.wallet_address = wallet
            user.wallet_verified = True
            user.save()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

# CHARITY VIEWS

def charity_dashboard(request):
    """Charity dashboard showing received donations"""
    charity = request.user.charity_admin
    donations = Donation.objects.filter(charity=charity)
    
    return render(request, "charity/dashboard.html", {
        "donations": donations,
        "charity": charity
    })
```

---

## 12. SECURITY ARCHITECTURE

### 12.1 Security Mechanisms

| Layer | Mechanism | Implementation |
|-------|-----------|-----------------|
| **Cryptographic** | Ethereum Message Signing | EIP-191 standard |
| **Authentication** | MetaMask Wallet Verification | verify_signature() function |
| **Authorization** | Role-based Access Control | @login_required decorators |
| **Data Integrity** | Message + Signature Storage | Stored with every donation |
| **Fraud Prevention** | AML Checks | Threshold + Frequency limits |
| **Database** | Custom User Model | AbstractUser extension |
| **Session** | Django Sessions | CSRF protection via middleware |

### 12.2 Key Security Code

```python
# Signature Verification - Core Security
def verify_signature(message, signature, wallet_address):
    """
    Uses Ethereum's EIP-191 standard:
    - Prefixes message with "\x19Ethereum Signed Message:" 
    - Recovers wallet address from signature
    - Compares with provided address
    """
    w3 = Web3()
    message_hash = encode_defunct(text=message)
    recovered_address = w3.eth.account.recover_message(
        message_hash, 
        signature=signature
    )
    return recovered_address.lower() == wallet_address.lower()

# Wallet Uniqueness Enforcement
if UserAccount.objects.filter(wallet_address__iexact=addr).exists():
    raise ValidationError("Wallet already registered")
if Charity.objects.filter(wallet_address__iexact=addr).exists():
    raise ValidationError("Charity wallet already exists")

# AML Fraud Detection
flagged = check_aml(donor.username, amount, recent_donations)
```

### 12.3 Data Flow Security

```
User Input (Frontend)
        ↓
Validation (Web3.js)
        ↓
MetaMask Signing
        ↓
Signed Data (Backend)
        ↓
Signature Verification (verify_signature)
        ↓
AML Check (check_aml)
        ↓
Database Storage (Encrypted Password)
```

---

## 13. DATABASE SETUP & DEPLOYMENT

### 13.1 Initial Setup

```bash
# Navigate to backend
cd backend/

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample charities (optional)
python create_charities.py

# Run development server
python manage.py runserver
```

### 13.2 Requirements.txt
```
Django==4.2.0
djangorestframework==3.14.0
web3==6.0.0
eth-account==0.9.5
eth-keys==0.4.0
eth-utils==2.0.0
```

### 13.3 Django Admin Interface

```python
# admin.py - Shows donation statistics
@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "wallet_address", 
                   "wallet_verified", "total_donated")
    list_filter = ("wallet_verified", "created_at")
    fieldsets = (
        ('Basic Info', {'fields': ('username', 'email')}),
        ('Wallet Info', {'fields': ('wallet_address', 'wallet_verified', 
                                    'total_donated')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
    )

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("donor", "charity", "amount", "flagged", 
                   "verified", "created_at")
    list_filter = ("flagged", "verified", "created_at")
    search_fields = ("donor__username", "charity__name")
```

---

## 14. KEY FEATURES & ADVANTAGES

### 14.1 Core Features

1. **Transparent Donations**
   - All donations recorded immutably
   - Message + signature stored for verification
   - Traceable end-to-end

2. **Cryptographic Verification**
   - Uses Ethereum's proven cryptography
   - No central authority needed
   - Users control their own keys (via MetaMask)

3. **Dual-Role System**
   - Donors verify identity via wallet
   - Charities register via MetaMask signature
   - Mixed password + cryptographic auth

4. **Fund Control**
   - Donors approve fund releases
   - Charities request specific amounts
   - Audit trail of all requests

5. **Fraud Prevention**
   - AML thresholds (100K ETH max per transaction)
   - Frequency limits (max 5 donations)
   - Flagged transactions for review

### 14.2 Advantages Over Traditional Systems

| Traditional | Our System |
|------------|-----------|
| Centralized authority | Cryptographic verification |
| Trust required | Trust verified with signatures |
| Manual audit | Immutable blockchain records |
| Single point of failure | Distributed verification |
| Difficult to prove donations | Cryptographically proven donations |

---

## 15. IMPORTANT CODE SNIPPETS REFERENCE

### 15.1 Quick Reference Table

| Functionality | File | Key Function/Class |
|--------------|------|------------------|
| User Registration | auth_views.py | UserSignUpForm.save() |
| Charity Registration | auth_views.py | CharitySignUpForm.save() |
| Signature Verification | signature_verify.py | verify_signature() |
| Donation Processing | views.py | donate() view |
| AML Detection | aml.py | check_aml() |
| Fund Requests | auth_views.py | handle_fund_request() |
| Wallet Update | auth_views.py | update_wallet() |
| MetaMask Connect | donate.html | connectMetaMask() JS |

### 15.2 Critical Imports

```python
# Backend
from web3 import Web3
from eth_account.messages import encode_defunct
from django.contrib.auth.models import AbstractUser
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

# JavaScript (Frontend)
// Web3.js for MetaMask
<script src="https://cdn.jsdelivr.net/npm/web3@1.10.0/dist/web3.min.js"></script>
```

---

## 16. TROUBLESHOOTING & COMMON ISSUES

### 16.1 Common Problems

| Issue | Cause | Solution |
|-------|-------|----------|
| **"Please select your registered wallet"** | Account mismatch | Click "Switch MetaMask Account" |
| **"Wallet already registered"** | Duplicate wallet address | Use different MetaMask account |
| **MetaMask not connecting** | Extension not installed | Install MetaMask extension |
| **Signature verification failed** | Wrong message signed | Ensure MetaMask signs exact message |
| **Database migration errors** | SQLite locked | Stop server, delete db, re-migrate |
| **Charity not appearing** | verified=False | Charity signup must pass verification |

### 16.2 Admin Debug Checks

```python
# Check wallets
UserAccount.objects.filter(wallet_verified=True)

# Check flagged donations
Donation.objects.filter(flagged=True)

# Check charities
Charity.objects.filter(verified=True)

# Delete and rebuild DB
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
```

---

## 17. FUTURE ENHANCEMENTS

1. **Smart Contract Integration**
   - Deploy Zakat.sol to testnet
   - Actual fund transfers on-chain
   - Real ETH/cryptocurrency handling

2. **Advanced AML**
   - Blockchain transaction analysis
   - Cross-reference donor addresses
   - Integration with external AML services

3. **Multi-Signature Wallet**
   - Require 2-of-3 approvals for large amounts
   - Time-locked releases
   - Emergency freeze mechanisms

4. **Frontend Enhancements**
   - React/Vue.js rewrite
   - Real-time donation tracking
   - Analytics dashboard
   - Mobile app

5. **Scaling**
   - Multi-chain support (Polygon, Arbitrum)
   - Layer 2 scaling solutions
   - Batch processing for gas optimization

---

## 18. PROJECT STRUCTURE DIAGRAM

```
transparent_donation_sys/
├── README.md
├── requirements.txt
├── PROJECT_SUMMARY.md (this file)
│
├── backend/
│   ├── db.sqlite3                    # SQLite database
│   ├── manage.py
│   ├── zakat_project/
│   │   ├── __init__.py
│   │   ├── settings.py               # Django configuration
│   │   ├── urls.py                   # URL routing
│   │   └── wsgi.py
│   │
│   └── zakat_app/
│       ├── __init__.py
│       ├── admin.py                  # Django admin config
│       ├── apps.py
│       ├── models.py                 # Database models
│       ├── views.py                  # Main views
│       ├── auth_views.py             # Authentication views
│       ├── urls.py                   # App URL routes
│       ├── serializers.py            # REST serializers
│       ├── signature_verify.py       # Crypto verification
│       ├── blockchain.py             # Blockchain integration
│       ├── aml.py                    # AML checks
│       ├── tests.py
│       └── migrations/
│           └── 0001_initial.py       # Database migrations
│
├── blockchain/
│   ├── contracts/
│   │   └── Zakat.sol                 # Smart contract
│   └── scripts/
│       └── deploy.js                 # Deployment script
│
└── frontend/
    ├── static/
    │   ├── css/
    │   └── js/
    └── templates/
        ├── base.html
        ├── index.html
        ├── success.html
        ├── auth/
        │   ├── user_login.html
        │   ├── user_signup.html
        │   ├── charity_login.html
        │   └── charity_signup.html
        ├── donor/
        │   ├── dashboard.html
        │   ├── donate.html
        │   └── wallet.html
        └── charity/
            └── dashboard.html
```

---

## 19. CONCLUSION

This **Blockchain-Based Transparent Zakat Distribution System** successfully combines:
- **Modern Web Development** (Django, JavaScript, MetaMask)
- **Cryptographic Security** (Ethereum signatures, EIP-191)
- **Financial Compliance** (AML checks, fraud detection)
- **User Experience** (Intuitive dashboards, clear workflows)

The system provides a **trustless, transparent, and traceable** solution for charitable donations while leveraging blockchain technology's immutability and security properties.

---

## 20. APPENDIX - IMPORTANT CODE FILES

### A. Complete Settings.py
```python
AUTH_USER_MODEL = 'zakat_app.UserAccount'
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "zakat_app",
]
```

### B. All URL Routes
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('user/signup/', user_signup, name='user_signup'),
    path('user/login/', user_login, name='user_login'),
    path('user/logout/', user_logout, name='user_logout'),
    path('charity/signup/', charity_signup, name='charity_signup'),
    path('charity/login/', charity_login, name='charity_login'),
    path('charity/logout/', charity_logout, name='charity_logout'),
    path('donor/dashboard/', donor_dashboard, name='donor_dashboard'),
    path('donor/wallet/', donor_wallet, name='donor_wallet'),
    path('donor/donate/', donate, name='donate'),
    path('charity/dashboard/', charity_dashboard, name='charity_dashboard'),
    path('api/update-wallet/', update_wallet, name='update_wallet'),
    path('success/', success_page, name='success'),
    path('handle-fund-request/<int:request_id>/', handle_fund_request, name='handle_fund_request'),
]
```

---

**Document Created:** April 2026 | **Framework:** Django 4.2 | **Blockchain:** Ethereum | **Tech:** Web3.py, MetaMask
