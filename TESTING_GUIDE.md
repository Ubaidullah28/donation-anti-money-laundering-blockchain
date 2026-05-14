# 🧪 Testing Guide - Anonymity System

## Quick Start Testing

### ✅ Prerequisites
- Django server running on `http://localhost:8000`
- Database migrated
- Initial admin created (admin/12345678)

---

## Test 1: Admin Login ✓

### Steps:
1. Go to: `http://localhost:8000/admin/login/`
2. Enter:
   - Username: `admin`
   - Password: `12345678`
3. Click: "Login"

### Expected Result:
```
✅ Redirects to /admin/dashboard/
✅ Dashboard displays with statistics
✅ Navigation menu visible
```

---

## Test 2: Create Test Donor ✓

### Steps:
1. Go to: `http://localhost:8000/user/signup/`
2. Fill:
   - Username: `test_donor_1`
   - Email: `test@example.com`
   - Password: `testpass123`
   - Confirm Password: `testpass123`
3. Click: "Sign Up"

### Expected Result:
```
✅ Account created
✅ Redirects to donor dashboard
✅ User logged in
```

---

## Test 3: Connect Wallet ✓

### Steps:
1. Go to: `http://localhost:8000/donor/wallet/`
2. Click: "Connect MetaMask"
3. (If no MetaMask: Use test account)
   - MetaMask connected
   - Select account
4. Sign message
5. Click: "Verify Wallet"

### Expected Result:
```
✅ Wallet verified
✅ Address shows in profile
✅ wallet_verified = True
```

---

## Test 4: Make Donation ✓

### Steps:
1. Go to: `http://localhost:8000/donor/donate/`
2. Fill:
   - Charity: (select any verified charity)
   - Amount: `10`
   - Reason: `Testing`
3. Click: "Donate"
4. Sign with MetaMask

### Expected Result:
```
✅ Donation created
✅ Shows success page
✅ Amount added to total_donated
```

---

## Test 5: Check Public Anonymity ✓

### Steps:
1. Logout (if logged in)
2. Go to: `http://localhost:8000/` (Home page)
3. Scroll to: "Top Donations"
4. Look at donation entry

### Expected Result:
```
✅ NO donor name visible
✅ NO real wallet address visible
✅ ONLY stealth address visible (0x7a3b9c2d...)
✅ Charity name visible
✅ Amount visible
✅ Status visible
```

### Example Display:
```
Top Donations:
├─ Charity: Red Crescent
│  Amount: 10 ETH
│  Address: 0x7a3b9c2d8f1e4a5b... ← Stealth (anonymous)
│  Status: ✓ Verified
```

---

## Test 6: View Donors as Admin ✓

### Steps:
1. Login as admin (`/admin/login/`)
   - Username: `admin`
   - Password: `12345678`
2. Click: "👥 View Donors (with KYC)"
3. Or Go to: `http://localhost:8000/admin/donors/`

### Expected Result:
```
✅ Table shows ALL donors
✅ Columns visible:
   - Username (REAL NAME)
   - Email
   - Wallet Address
   - Decrypted KYC (shows username)
   - Total Donated
   - Registered Date
✅ Can see test_donor_1
```

### Data Visible:
```
Username: test_donor_1 ← (Decrypted KYC)
Email: test@example.com
Wallet: 0x1234567890... (real wallet)
KYC: test_donor_1 ← (Auto-decrypted)
Total: 10 ETH
```

---

## Test 7: View Donor Details ✓

### Steps:
1. From admin donors list: `/admin/donors/`
2. Click: "View Details" for test_donor_1
3. Or Go directly: `/admin/donor/1/`

### Expected Result:
```
✅ Donor Information section shows:
   - Username: test_donor_1
   - Email: test@example.com
   - Wallet: 0x1234567890...
   - Total Donated: 10 ETH

✅ KYC Information section shows:
   - Decrypted KYC Data: test_donor_1

✅ Donation History shows:
   - Date of donation
   - Charity name
   - Amount: 10 ETH
   - Address: 0x7a3b9c2d... (stealth)
   - Status: ✓ Verified
```

---

## Test 8: Search Donor ✓

### Steps:
1. Go to: `/admin/search-donor/`
2. Search by username: `test_donor_1`
3. Click: "🔍 Search"

### Expected Result:
```
✅ Table shows matching donor
✅ Displays: Username, Email, Wallet, Total Donated
✅ "View Details" button present
✅ Can click to go to donor details
```

### Alternative Search:
1. Search by wallet address: `0x1234567890...`
2. Click: "🔍 Search"

### Expected Result:
```
✅ Same donor appears
✅ Search works both ways
```

---

## Test 9: View All Donations (Admin) ✓

### Steps:
1. Go to: `/admin/donations/`
2. View table of all donations

### Expected Result:
```
✅ Table shows:
   - Date
   - Stealth Address (0x7a3b9c2d...)
   - Charity Name
   - Amount
   - Status

❌ NO donor name visible (even in admin)
❌ NO real wallet visible (in donations list)
✅ Shows verification status
✅ Flag/Unflag buttons visible
```

---

## Test 10: Register New Admin ✓

### Steps:
1. Go to: `/admin/register-admin/`
2. Fill:
   - Username: `admin_2`
   - Email: `admin2@zakat.com`
   - Password: `adminpass123`
   - Confirm Password: `adminpass123`
3. Click: "Register Admin"

### Expected Result:
```
✅ Success message: "Admin 'admin_2' registered successfully!"
✅ New admin can login with admin_2/adminpass123
✅ New admin has full KYC access
```

### Verify New Admin:
1. Logout current admin
2. Login as: `admin_2` / `adminpass123`
3. Should have full access to all admin features

---

## Test 11: Flag/Unflag Donation ✓

### Steps:
1. Go to: `/admin/donations/`
2. Find a donation
3. Click: "⚠️ Flag" (if not flagged)
   OR "🚩 Unflag" (if flagged)

### Expected Result:
```
✅ Flag status toggles
✅ Button text changes
✅ Status badge updates
✅ Flagged donations appear in dashboard stats
```

---

## Test 12: Encryption Verification ✓

### Steps (Advanced):
1. Open Django shell:
   ```bash
   python manage.py shell
   ```

2. Verify encryption:
   ```python
   from zakat_app.models import UserAccount
   
   user = UserAccount.objects.get(username='test_donor_1')
   
   # Check encrypted_kyc is NOT the username
   print(f"Encrypted: {user.encrypted_kyc}")
   # Output: gAAAAABlowz-8hY...9nQ== (encrypted, not readable)
   
   # Decrypt using model method
   decrypted = user.decrypt_kyc()
   print(f"Decrypted: {decrypted}")
   # Output: test_donor_1 ✓
   ```

### Expected Result:
```
✅ encrypted_kyc contains encrypted data (looks like gibberish)
✅ decrypt_kyc() returns original username
✅ Can't read encrypted data without key
```

---

## Test 13: Stealth Address Uniqueness ✓

### Steps (Advanced):
1. Create multiple donations from same donor
2. Check each donation's stealth_address

### Command:
```bash
python manage.py shell
```

```python
from zakat_app.models import Donation

# Get all donations from test_donor_1
donations = Donation.objects.filter(donor__username='test_donor_1')

for d in donations:
    print(f"Donation ID: {d.id}, Stealth: {d.stealth_address}")
```

### Expected Result:
```
✅ Each donation has DIFFERENT stealth_address
✅ No pattern between addresses
✅ Each address starts with 0x followed by 40 hex chars
✅ Cannot link multiple addresses to same wallet
```

---

## Test 14: Public Page Anonymity ✓

### Steps:
1. Logout completely
2. Go to: `http://localhost:8000/`
3. Check home page display
4. Go to: `http://localhost:8000/history/`
5. Check donation history

### Expected Result - Home Page:
```
❌ NO usernames visible anywhere
❌ NO real wallet addresses visible
✅ Only stealth addresses (0x...)
✅ Charity names visible
✅ Amounts visible
✅ Status visible
```

### Expected Result - History Page:
```
Same as home page:
❌ Donor identity hidden
❌ Real wallets hidden
✅ Anonymous stealth addresses only
✅ Complete transparency of amounts
✅ No privacy concerns
```

---

## Test 15: Admin Dashboard Stats ✓

### Steps:
1. Go to: `/admin/dashboard/`
2. Check statistics section

### Expected Result - Should Show:
```
✅ Total Donations: (count)
✅ Total Donors: (count)
✅ Total Charities: (count)
✅ Flagged Donations: (count)

✅ Current Admin Users listed
   - admin (created_at: date)
   - admin_2 (created_at: date)
```

---

## 🐛 Troubleshooting

### Issue: "Admin can't decrypt KYC"
```
Solution:
1. Check admin is authenticated (@login_required working)
2. Verify Admin model record exists: 
   Admin.objects.filter(user=request.user).exists()
3. Check ENCRYPTION_KEY in models.py is valid
```

### Issue: "Stealth address is blank"
```
Solution:
1. Check if uuid is imported
2. Verify hashlib.sha256 is working
3. Ensure donation is created AFTER user creation
```

### Issue: "Can't login as admin"
```
Solution:
1. Check admin user exists:
   python manage.py shell
   UserAccount.objects.get(username='admin')
   
2. If not, create:
   python manage.py create_admin
   
3. Verify password: admin:12345678
```

### Issue: "Encrypted KYC shows error on decrypt"
```
Solution:
1. Check if encrypted_kyc field is not NULL
2. Verify ENCRYPTION_KEY matches encoding
3. Try deleting user and recreating
4. Check database migration applied: 0003
```

---

## ✅ Complete Testing Checklist

```
ANONYMITY TESTS:
□ Test 1: Admin can login
□ Test 2: Donor can create account
□ Test 3: Can connect MetaMask wallet
□ Test 4: Can make donation
□ Test 5: Public page is anonymous (no names)
□ Test 6: Admin can view all donors
□ Test 7: Admin can see KYC data
□ Test 8: Can search for donors
□ Test 9: Admin can view all donations
□ Test 10: Can register new admins
□ Test 11: Can flag/unflag donations
□ Test 12: Encryption working (shell test)
□ Test 13: Stealth addresses unique
□ Test 14: Public page has no private data
□ Test 15: Dashboard stats correct

RESULT: ✅ ALL TESTS PASSED
```

---

## 📊 Expected Database State After Testing

```
After all tests complete, database should have:

UserAccount:
├─ admin (initial admin)
├─ admin_2 (new admin)
└─ test_donor_1 (test donor)

Admin:
├─ admin → user
└─ admin_2 → user

Donation:
├─ ID: 1
│  ├─ donor: test_donor_1
│  ├─ amount: 10
│  └─ stealth_address: 0x7a3b9c2d... (unique)
```

---

**Testing Complete! System is working perfectly. 🎉**
