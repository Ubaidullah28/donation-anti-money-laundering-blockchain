#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zakat_project.settings')
django.setup()

from zakat_app.models import Charity

# Clear existing charities
Charity.objects.all().delete()

# Create sample charities
charities_data = [
    {
        'name': 'Red Crescent',
        'wallet_address': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
        'description': 'Islamic humanitarian organization providing aid and relief',
        'verified': True
    },
    {
        'name': 'Islamic Relief',
        'wallet_address': '0x8ba1f109551bD432803012645ac136ddd64DBA72',
        'description': 'Global humanitarian organization supporting vulnerable populations',
        'verified': True
    },
    {
        'name': 'Zakat Foundation',
        'wallet_address': '0x4B20993Bc481177ec7E8f571ceCaE8A9e22C02db',
        'description': 'Dedicated to transparent zakat distribution and community development',
        'verified': True
    }
]

for data in charities_data:
    charity = Charity.objects.create(**data)
    print(f"✓ Created: {charity.name}")

print(f'\n✓ Total charities: {Charity.objects.count()}')
