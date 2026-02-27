import logging
from django.utils import timezone
from datetime import timedelta
from tickets.models import Sale

logger = logging.getLogger(__name__)

def update_payout_status_task():
    """
    Background task to update payout status 7 days after event date
    """
    try:
        # Get all sales without payout date
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
                        logger.info(f'Updated sale {sale.id} - payout completed')
            except Exception as e:
                logger.error(f'Error processing sale {sale.id}: {str(e)}')
        
        logger.info(f'Payout status update completed - {updated_count} sales updated')
        return updated_count
    except Exception as e:
        logger.error(f'Error in update_payout_status_task: {str(e)}')
        return 0
