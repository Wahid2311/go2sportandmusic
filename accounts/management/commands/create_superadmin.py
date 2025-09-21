from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a superadmin account'

    def handle(self, *args, **options):
        if User.objects.filter(is_superadmin=True).exists():
            self.stdout.write(self.style.WARNING('Superadmin already exists'))
            return

        try:
            user = User.objects.create_superuser(
                email=settings.SUPERADMIN_EMAIL,
                password=settings.SUPERADMIN_PASSWORD,
                first_name='Super',
                last_name='Admin',
                phone='+10000000000',
                user_type='Reseller',
                country='US',
                city='Admin City',
                street_no='1 Admin Street',
                social_media_link='https://admin.example',
                verified_seller=True
            )
            self.stdout.write(self.style.SUCCESS(
                f'Superadmin created successfully! Email: {user.email}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Error creating superadmin: {str(e)}'
            ))