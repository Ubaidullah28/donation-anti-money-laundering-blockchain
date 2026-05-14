from django.db import models
from django.contrib.auth.models import AbstractUser
from cryptography.fernet import Fernet
import base64

# Generate a proper encryption key (44 bytes base64 = 32 bytes decoded)
SECRET_KEY_BYTES = b'ThisIsA32ByteSecretKeyForEncryption!!'[:32]
ENCRYPTION_KEY = base64.urlsafe_b64encode(SECRET_KEY_BYTES)

class UserAccount(AbstractUser):
    """Extended User model for donors"""
    wallet_address = models.CharField(max_length=200, blank=True, null=True)
    wallet_verified = models.BooleanField(default=False)
    total_donated = models.FloatField(default=0)
    encrypted_kyc = models.TextField(blank=True, null=True)  # Encrypted KYC data
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Encrypt KYC data if present
        if self.username and not self.encrypted_kyc:
            cipher = Fernet(ENCRYPTION_KEY)
            self.encrypted_kyc = cipher.encrypt(self.username.encode()).decode()
        super().save(*args, **kwargs)

    def decrypt_kyc(self):
        if self.encrypted_kyc:
            cipher = Fernet(ENCRYPTION_KEY)
            return cipher.decrypt(self.encrypted_kyc.encode()).decode()
        return None

    @property
    def is_admin(self):
        return hasattr(self, 'admin')

    def __str__(self):
        return f"Donor: {self.username}"


class Charity(models.Model):
    """Charity organization account"""
    name = models.CharField(max_length=200)
    admin_user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='charity_admin', null=True, blank=True)
    wallet_address = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    verified = models.BooleanField(default=False)
    total_spent = models.FloatField(default=0, help_text="Total amount spent from unlocked funds")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_unlocked_funds(self):
        """Total unlocked funds available for spending"""
        return sum(donation.unlocked_balance for donation in self.donations.all())

    @property
    def available_balance(self):
        """Available balance for spending (unlocked - spent)"""
        return self.total_unlocked_funds - self.total_spent

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Charities"


class Donation(models.Model):
    donor = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='donations', null=True, blank=True)
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, related_name='donations', null=True, blank=True)
    wallet_address = models.CharField(max_length=200, blank=True, null=True)
    stealth_address = models.CharField(max_length=200, blank=True, null=True)  # Unique address for anonymity
    amount = models.FloatField()
    reason = models.TextField(blank=True, help_text="Reason for donation")
    flagged = models.BooleanField(default=False)
    signature = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    locked_balance = models.FloatField(default=0, help_text="Amount still locked, not unlocked to charity")
    unlocked_balance = models.FloatField(default=0, help_text="Amount unlocked to charity")
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        # Initialize locked balance to full amount on creation
        if not self.pk and self.amount:
            self.locked_balance = self.amount
        super().save(*args, **kwargs)

    def unlock_amount(self, amount):
        """Unlock a portion of the donation"""
        if amount <= self.locked_balance:
            self.locked_balance -= amount
            self.unlocked_balance += amount
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.donor.username if self.donor else 'Unknown'} -> {self.charity.name if self.charity else 'Unknown'}: {self.amount} ETH"


class FundUnlockRequest(models.Model):
    """Request from charity to unlock donated funds"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, related_name='fund_requests')
    donor = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='fund_requests_received')
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    amount = models.FloatField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # When status changes to approved, unlock the balance
        if self.pk:
            old_instance = FundUnlockRequest.objects.get(pk=self.pk)
            if old_instance.status != 'approved' and self.status == 'approved':
                # Unlock the amount from the donation
                self.donation.unlock_amount(self.amount)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.charity.name} requesting {self.amount} ETH from {self.donor.username}"


class CharityExpense(models.Model):
    """Expense record for charity spending unlocked funds"""
    CATEGORY_CHOICES = [
        ('bills', 'Bills and Utilities'),
        ('supplies', 'Supplies and Equipment'),
        ('services', 'Services and Maintenance'),
        ('other', 'Other Expenses'),
    ]
    
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, related_name='expenses')
    amount = models.FloatField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField(help_text="Detailed description of the expense")
    transaction_hash = models.CharField(max_length=200, blank=True, null=True, help_text="Blockchain transaction hash if applicable")
    approved_by_admin = models.BooleanField(default=False, help_text="Admin approval required for large expenses")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            # creation: reserve unlocked funds for this expense
            if self.amount > self.charity.available_balance:
                raise ValueError("Insufficient unlocked funds available")
            self.charity.total_spent += self.amount
            self.charity.save()
        else:
            # update: avoid re-checking funds for an already reserved expense
            old_instance = CharityExpense.objects.get(pk=self.pk)
            if self.amount != old_instance.amount:
                delta = self.amount - old_instance.amount
                if delta > 0 and delta > self.charity.available_balance:
                    raise ValueError("Insufficient unlocked funds available")
                self.charity.total_spent += delta
                self.charity.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.charity.name} - {self.category}: {self.amount} ETH"


class Request(models.Model):
    """Old fund request model - kept for compatibility"""
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, null=True, blank=True)
    purpose = models.TextField()
    amount = models.FloatField()
    recipient_wallet = models.CharField(max_length=200)
    approvals = models.IntegerField(default=0)
    authority_approved = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.charity.name if self.charity else 'Unknown'} - {self.purpose}: {self.amount} ETH"


class Admin(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    can_decrypt = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Admin: {self.user.username}"