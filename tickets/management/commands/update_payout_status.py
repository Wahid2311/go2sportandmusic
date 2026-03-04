from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from tickets.models import Sale

class Command(BaseCommand):
    help = 'Update payout status to completed 7 days after event date'
    
    def handle(self, *args, **options):
        # Get all sales with Processing status
        sales = Sale.objects.filter(payout_date__isnull=True)
        
        updated_count = 0
        today = timezone.now().date()
        
        for sale in sales:
            try:
                # Get the event date from the order
                event_date = sale.order.event_date
                
                if event_date:
                    # Calculate the payout date (7 days after event)
                    payout_date = event_date + timedelta(days=7)
                    
                    # If today is on or after the payout date, mark as completed
                    if today >= payout_date:
                        sale.payout_date = today
                        sale.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Updated sale {sale.id} - payout completed'
                            )
                        )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing sale {sale.id}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} sales')
        )
