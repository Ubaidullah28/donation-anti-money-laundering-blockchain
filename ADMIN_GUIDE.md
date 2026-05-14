# 🎯 QUICK START GUIDE - Anonymity System

## 🚀 Getting Started

### Step 1: Start the Server
```bash
cd backend
python manage.py runserver
```
Server runs at: `http://localhost:8000`

---

## 👨‍💻 Admin Panel Access

### Login Credentials (Initial)
```
URL: http://localhost:8000/admin/login/
Username: admin
Password: 12345678
```

### Admin Capabilities
After login at `/admin/login/`, you get access to:

1. **📊 Dashboard** (`/admin/dashboard/`)
   - Total donations count
   - Total unique donors
   - Total charities
   - Flagged donations for review
   - List of all admins

2. **👥 View Donors** (`/admin/donors/`)
   - See ALL donors with **decrypted KYC data**
   - Shows: Username, Email, Real Wallet, Encrypted KYC (decrypted), Total Donated
   - Click "View Details" for detailed donation history per donor

3. **💰 View All Donations** (`/admin/donations/`)
   - Blockchain transparency view
   - Shows: Date, Stealth Address, Charity, Amount, Status
   - Flag/unflag donations for investigation
   - Public addresses only (donors anonymous)

4. **🏢 View Charities** (`/admin/charities/`)
   - See all registered charities
   - Wallet addresses, verification status, total donations

5. **🔍 Search Donor** (`/admin/search-donor/`)
   - Search by username or wallet address
   - Quick access to donor KYC info

6. **➕ Register New Admin** (`/admin/register-admin/`)
   - Existing admins can create new admins
   - New admins get full KYC decryption access

---

## 👤 Donor/User Workflow

### 1. Create Account (Anonymous Donor)
- Go to: `http://localhost:8000/user/signup/`
- Fill: Username, Email, Password
- Create account (no KYC data needed upfront)

### 2. Connect MetaMask Wallet
- Go to: `/donor/wallet/`
- Click "Connect MetaMask"
- Sign message to verify ownership
- Wallet verified

### 3. Make Donation
- Go to: `/donor/donate/`
- Select charity
- Enter amount
- Sign with MetaMask
- **Donation appears with STEALTH ADDRESS on public page** ✅

---

## 🔒 Anonymity Guarantee

### Public View (Home Page / History)
```
Anyone can see:
❌ Donor Name
❌ Donor Email
❌ Real Wallet Address
✅ Donation Amount
✅ Stealth Address (unique, anonymous)
✅ Charity Name
✅ Status (Verified/Pending)
```

### Admin View (After Login)
```
Admin can see:
✅ Donor Name
✅ Donor Email
✅ Real Wallet Address
✅ Donation Amount
✅ Stealth Address
✅ Charity Name
✅ Encrypted KYC (Decryptable)
✅ Full donation history
```

---

## 🔍 Government Verification Scenario

**Scenario**: "Who donated 50 ETH to Red Crescent?"

### Step 1: Admin Logs In
```
URL: http://localhost:8000/admin/login/
Username: admin
Password: 12345678
```

### Step 2: Go to View Donations
```
Click: 💰 View All Donations
Filter by charity: Red Crescent
Filter by amount: 50 ETH
```

### Step 3: Find the Donation
- See stealth address and donation details
- Click on donor or use search to find

### Step 4: View Donor Details
- Click "View Details" on the donation
- See **Decrypted KYC** with real donor identity
- Access full donation history
- Complete audit trail available

### Step 5: Provide Information
- Admin can now provide government with:
  - Real donor name
  - Email address
  - Wallet address
  - All donations by this donor
  - AML flags (if any)

---

## 🛠️ Technical Details

### Stealth Address Generation
```python
stealth_address = "0x" + SHA256(uuid + wallet_address + donor_id).hex()[:40]
```
- **Unique per donation** (not reused)
- **Non-linkable** to real wallet
- **Verifiable** by admin with encryption key

### KYC Encryption
```python
encrypted_kyc = Fernet.encrypt(username)
# Uses symmetric encryption (Fernet/AES-128)
# Stored in database, only decryptable by admins
```

### Authentication
- **Donors**: MetaMask signature verification
- **Admins**: Django session authentication
- **Charities**: Charity admin account system

---

## 📊 Database Models

### Admin Model
```
- user: Link to UserAccount
- can_decrypt: Boolean (permission)
- created_at: DateTime
```

### UserAccount (Enhanced)
```
- ... (existing fields)
- encrypted_kyc: TextField (encrypted username)
- decrypt_kyc(): method to decrypt
```

### Donation (Enhanced)
```
- ... (existing fields)
- stealth_address: CharField (anonymous address)
```

---

## ✅ Testing Checklist

- [ ] Admin can login with admin/12345678
- [ ] Admin can view all donors with KYC
- [ ] Admin can search for donors
- [ ] Admin can decrypt KYC info
- [ ] Public page shows only stealth addresses
- [ ] Donors remain anonymous publicly
- [ ] New admins can be registered
- [ ] Donations can be flagged/unflagged
- [ ] Charity list accessible
- [ ] Donation history viewable per donor

---

## 🚨 Important Notes

1. **Encryption Key** is hardcoded in `models.py` for demo
   - In production: Store in environment variables
   - In production: Use proper key management (AWS KMS, HashiCorp Vault, etc.)

2. **Stealth Addresses** are for blockchain anonymity
   - Not linked to real wallet on public view
   - Linkable only in admin panel

3. **Admin Access** is sensitive
   - Audit logs recommended for production
   - Role-based access control (RBAC) can be enhanced
   - Multiple admin levels possible

4. **AML Checks** still run on real donor data
   - Flagged donations visible to admin
   - Privacy + Compliance maintained

---

## 📞 Admin Panel URL Map

| Feature | URL |
|---------|-----|
| Login | `/admin/login/` |
| Logout | `/admin/logout/` |
| Dashboard | `/admin/dashboard/` |
| View Donors | `/admin/donors/` |
| Donor Details | `/admin/donor/<id>/` |
| View Donations | `/admin/donations/` |
| View Charities | `/admin/charities/` |
| Flag Donation | `/admin/flag/<donation_id>/` |
| Register Admin | `/admin/register-admin/` |
| Search Donor | `/admin/search-donor/` |

---

## 🎓 Learning Outcomes

This system demonstrates:
1. ✅ **Encryption in practice** (Fernet symmetric)
2. ✅ **Role-based access control** (admin vs donor)
3. ✅ **Zero-knowledge proof concepts** (admin knows identity secretly)
4. ✅ **Stealth addresses** (blockchain anonymity)
5. ✅ **KYC/AML compliance** (regulatory balance)
6. ✅ **Secure authentication** (MetaMask + Django)

---

**Ready to test? Start the server and go to `http://localhost:8000`! 🚀**
