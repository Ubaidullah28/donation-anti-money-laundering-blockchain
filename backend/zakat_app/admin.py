from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import UserAccount, Donation, Request, Charity, FundUnlockRequest


@admin.register(UserAccount)
class UserAccountAdmin(UserAdmin):
    list_display = ("username", "email", "wallet_address", "wallet_verified", "total_donated")
    list_filter = ("wallet_verified", "created_at")
    fieldsets = UserAdmin.fieldsets + (
        ('Wallet Info', {'fields': ('wallet_address', 'wallet_verified', 'total_donated')}),
    )


@admin.register(Charity)
class CharityAdmin(admin.ModelAdmin):
    list_display = ("name", "admin_user", "wallet_address", "verified", "created_at")
    list_filter = ("verified", "created_at")
    search_fields = ("name", "wallet_address", "admin_user__username")


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("donor", "charity", "amount", "verified", "flagged", "created_at")
    list_filter = ("verified", "flagged", "created_at", "charity")
    search_fields = ("donor__username", "charity__name", "wallet_address")
    readonly_fields = ("signature",)


@admin.register(FundUnlockRequest)
class FundUnlockRequestAdmin(admin.ModelAdmin):
    list_display = ("charity", "donor", "amount", "status", "created_at")
    list_filter = ("status", "created_at", "charity")
    search_fields = ("charity__name", "donor__username")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ("charity", "purpose", "amount", "approvals", "authority_approved", "completed")
    list_filter = ("completed", "authority_approved", "charity")
    search_fields = ("purpose", "charity__name", "recipient_wallet")
