# ANONYMITY IMPLEMENTATION: Stealth Addresses + KYC Vault

## Overview
Implemented a hybrid anonymity system combining **Stealth Addresses** for public transactions and **Encrypted KYC Vault** for authorized admin access.

---

## 🏗️ Architecture

### Public Side (Blockchain Transparency)
- ✅ All donors remain **completely anonymous** on the public site
- ✅ Each donation appears with a **unique stealth address** (not linked to the donor)
- ✅ Home page shows only: Charity Name, Amount, Stealth Address, Status
- ✅ **No donor names or real wallet addresses** visible publicly

### Private Side (Admin Panel)
- ✅ Admins can **decrypt KYC records** to identify donors
- ✅ Full donor details visible: Username, Email, Real Wallet, Encrypted KYC
- ✅ Complete donation history per donor
- ✅ Stealth address tracking for audit trails

---

## 🔐 Database Schema Changes

### 1. **UserAccount Model** (Enhanced)
```python
- encrypted_kyc: TextField  # Stores encrypted username for KYC
- decrypt_kyc(): method     # Only admins can call this

Methods:
- save(): Auto-encrypts KYC data on creation
- decrypt_kyc(): Decrypts using Fernet cipher
```

### 2. **Donation Model** (Enhanced)
```python
- stealth_address: CharField  # Unique address for anonymity
- wallet_address: CharField   # Real wallet (admin-only visible)

Generation:
- stealth_address = hash(uuid + wallet_address + donor_id)
- Unique for each donation
```

### 3. **Admin Model** (NEW)
```python
- user: OneToOneField(UserAccount)
- can_decrypt: Boolean  # Permission to decrypt KYC
- created_at: DateTime
```

---

## 👤 Authentication & Authorization

### Initial Admin Account
```
Username: admin
Password: 12345678
Email: admin@zakat.com
```

### Admin Registration
- Existing admins can register new admins
- New admins get full KYC decryption access
- Access controlled via @login_required decorator

---

## 🛣️ URL Routes (Admin Panel)

```
/admin/login/                    # Admin login
/admin/logout/                   # Admin logout
/admin/dashboard/                # Main dashboard with stats
/admin/donors/                   # View all donors (with decrypted KYC)
/admin/donor/<id>/              # Detailed view of specific donor
/admin/donations/               # View all donations (public data only)
/admin/charities/               # View all charities
/admin/flag/<donation_id>/      # Flag/unflag donation for review
/admin/register-admin/          # Register new admin user
/admin/search-donor/            # Search donors by name or wallet
```

---

## 🎯 Flow Diagram

```
PUBLIC VIEW:
┌─────────────────────────────┐
│   Home Page / History Page  │
│  (Only Stealth Addresses)   │
│  • Donation Amount          │
│  • Stealth Address (anon)   │
│  • Charity Name             │
│  • Verification Status      │
└─────────────────────────────┘

ADMIN VIEW:
┌─────────────────────────────┐
│   Admin Panel               │
│  (Full KYC Access)          │
│  • Donor Name               │
│  • Email                    │
│  • Real Wallet              │
│  • Encrypted KYC (decrypt)  │
│  • Donation History         │
└─────────────────────────────┘

GOVERNMENT REQUEST SCENARIO:
┌─────────────────────────────┐
│ Govt: "Who donated 50 ETH?" │
└─────────────────────────────┘
         ↓
┌─────────────────────────────┐
│ Admin Panel: Search by      │
│ amount/charity/date         │
│ Find donation               │
└─────────────────────────────┘
         ↓
┌─────────────────────────────┐
│ Click donor → View Details  │
│ See decrypted KYC           │
│ Identify real donor         │
└─────────────────────────────┘
```

---

## 🔒 Security Features

### 1. **Encryption**
- Algorithm: Fernet (AES-128, HMAC)
- Key: Base64 URL-safe encoded
- Storage: Encrypted username in `encrypted_kyc` field
- Decryption: Only by authorized admins

### 2. **Authentication**
- MetaMask signature verification for donations
- Django authentication for admin login
- Session-based access control

### 3. **Anonymity**
- Stealth addresses generated using:
  - Random UUID
  - Wallet address hash
  - Donor ID
- Each donation gets unique address
- No linking between addresses

---

## 📊 Admin Dashboard Features

### Statistics
- Total Donations Count
- Total Unique Donors
- Total Registered Charities
- Flagged Donations (AML review)

### Management Tools
- View all donors with decrypted KYC
- Search donors by name/wallet
- View detailed donation history
- Flag/unflag donations for investigation
- Register additional admins
- View all charities

---

## 📝 Templates Created

```
frontend/templates/admin/
├── login.html                 # Admin login page
├── dashboard.html             # Main dashboard
├── view_donors.html          # All donors (with KYC)
├── donor_details.html        # Specific donor details
├── view_donations.html       # All donations (public view)
├── view_charities.html       # All charities
├── register_admin.html       # Register new admin
└── search_donor.html         # Search functionality
```

---

## 🚀 Installation & Setup

### 1. Install Dependencies
```bash
pip install cryptography
```

### 2. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Initial Admin
```bash
python manage.py create_admin
# Output: Username: admin, Password: 12345678
```

### 4. Access Admin Panel
```
URL: http://localhost:8000/admin/login/
Username: admin
Password: 12345678
```

---

## ✅ Implementation Checklist

- [x] Encryption model for KYC data
- [x] Stealth address generation in donations
- [x] Admin model with permissions
- [x] Admin authentication views
- [x] Admin dashboard
- [x] Donor viewing with KYC decryption
- [x] Donation history tracking
- [x] Admin registration system
- [x] Search functionality
- [x] Flag/unflag donations
- [x] Initial admin creation command
- [x] HTML templates for admin panel
- [x] Public page anonymization

---

## 🔄 User Workflows

### Scenario 1: Normal Donation (Public)
1. Donor logs in
2. Selects charity
3. Confirms MetaMask signature
4. Donation created with **stealth address**
5. Public page shows only: Amount + Stealth Address + Charity

### Scenario 2: Government Verification Request
1. Govt says: "Verify who donated to charity X"
2. Admin logs in → Admin Dashboard
3. Searches for donations to charity X
4. Clicks donation → Donor Details
5. Decrypts KYC → Reveals real donor identity
6. Accesses full donation history

### Scenario 3: Register New Admin
1. Existing admin at `/admin/register-admin/`
2. Fills in new username/password
3. New admin created with full KYC access
4. New admin can now login at `/admin/login/`

---

## 🔐 Privacy Guarantees

| Aspect | Public | Admin |
|--------|--------|-------|
| Donor Name | ❌ Hidden | ✅ Visible |
| Email | ❌ Hidden | ✅ Visible |
| Real Wallet | ❌ Hidden | ✅ Visible |
| Amount | ✅ Visible | ✅ Visible |
| Charity | ✅ Visible | ✅ Visible |
| Stealth Address | ✅ Visible | ✅ Visible |
| Encrypted KYC | ❌ N/A | ✅ Decryptable |

---

## 🎓 Educational Benefits

This implementation demonstrates:
1. **Encryption in practice** (Fernet symmetric encryption)
2. **Zero-knowledge proofs concept** (admin knows identity without public revelation)
3. **Role-based access control** (admin vs donor vs public)
4. **Blockchain anonymity patterns** (stealth addresses)
5. **Regulatory compliance** (KYC vault for authorities)

---

## 📌 Notes

- All KYC data is encrypted before storage
- Stealth addresses are unique per donation (not reused)
- Admin panel requires authentication
- AML checks still run on real donor data
- Donations marked as flagged visible in admin panel
- Home page updated to show only stealth addresses

---

**Status**: ✅ IMPLEMENTED AND READY FOR USE
