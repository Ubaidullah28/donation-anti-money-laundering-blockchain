from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from zakat_app.models import Admin

User = get_user_model()

class Command(BaseCommand):
    help = 'Create initial admin user with username: admin and password: 12345678'

    def handle(self, *args, **options):
        # Check if admin user already exists
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('Admin user already exists!'))
            return

        # Create admin user
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@zakat.com',
            password='12345678'
        )

        # Create Admin record
        Admin.objects.create(user=admin_user, can_decrypt=True)

        self.stdout.write(self.style.SUCCESS('Admin user created successfully!'))
        self.stdout.write(self.style.SUCCESS('Username: admin'))
        self.stdout.write(self.style.SUCCESS('Password: 12345678'))
