from django.test import TestCase

from .models import Charity, Donation


class CharityModelTest(TestCase):
    def test_charity_creation(self):
        charity = Charity.objects.create(name="Test Charity", wallet_address="0x1234567890123456789012345678901234567890")
        self.assertEqual(str(charity), "Test Charity")


class DonationModelTest(TestCase):
    def test_donation_creation(self):
        charity = Charity.objects.create(name="Test Charity", wallet_address="0x1234567890123456789012345678901234567890")
        donation = Donation.objects.create(
            donor_name="Alice",
            donor_wallet="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            charity=charity,
            amount="0.5",
        )
        self.assertIn("Alice", str(donation))
