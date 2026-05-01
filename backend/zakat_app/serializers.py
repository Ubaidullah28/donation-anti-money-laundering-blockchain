from rest_framework import serializers

from .models import Charity, Donation


class CharitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Charity
        fields = ["id", "name", "wallet_address", "description"]


class DonationSerializer(serializers.ModelSerializer):
    charity = CharitySerializer()

    class Meta:
        model = Donation
        fields = [
            "id",
            "donor_name",
            "donor_wallet",
            "charity",
            "amount",
            "transaction_hash",
            "created_at",
        ]

    def create(self, validated_data):
        charity_data = validated_data.pop("charity")
        charity, _ = Charity.objects.get_or_create(**charity_data)
        return Donation.objects.create(charity=charity, **validated_data)
