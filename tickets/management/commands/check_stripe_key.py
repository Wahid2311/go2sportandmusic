from django.core.management.base import BaseCommand
from django.conf import settings
import stripe

class Command(BaseCommand):
    help = 'Check the Stripe API key configuration'

    def handle(self, *args, **options):
        stripe_key = settings.STRIPE_SECRET_KEY
        
        self.stdout.write(f"STRIPE_SECRET_KEY set: {bool(stripe_key)}")
        if stripe_key:
            self.stdout.write(f"Key length: {len(stripe_key)}")
            self.stdout.write(f"Key starts with: {stripe_key[:20]}")
            self.stdout.write(f"Key ends with: {stripe_key[-10:]}")
            
            # Try to use it
            stripe.api_key = stripe_key
            try:
                account = stripe.Account.retrieve()
                self.stdout.write(self.style.SUCCESS(f"✓ Stripe authentication successful!"))
                self.stdout.write(f"Account ID: {account.id}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Stripe error: {str(e)}"))
        else:
            self.stdout.write(self.style.ERROR("STRIPE_SECRET_KEY not set"))
