#!/usr/bin/env python3
"""
Pricing Management Script
Manages dynamic pricing, price adjustments, and pricing strategies
"""

import os
import sys
import django
import traceback
import logging
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'go2events.settings')
django.setup()

from tickets.models import Ticket, Section
from events.models import Event
from django.utils import timezone
from django.db.models import Q, Avg, Count

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pricing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PricingManager:
    """Manages pricing strategies and adjustments"""
    
    def __init__(self):
        self.updated_count = 0
        self.error_count = 0
        self.price_adjustments = []
    
    def get_demand_level(self, ticket):
        """Calculate demand level based on availability and time to event"""
        try:
            if not ticket.event:
                return 'low'
            
            # Calculate days until event
            days_until = (ticket.event.date - timezone.now()).days
            
            # Get availability percentage
            if ticket.number_of_tickets > 0:
                availability_percent = (ticket.number_of_tickets / ticket.initial_tickets) * 100 if ticket.initial_tickets else 100
            else:
                availability_percent = 0
            
            # Determine demand level
            if days_until < 7:
                # Last minute - high demand
                if availability_percent < 20:
                    return 'very_high'
                elif availability_percent < 50:
                    return 'high'
                else:
                    return 'medium'
            elif days_until < 30:
                # Medium term
                if availability_percent < 30:
                    return 'high'
                else:
                    return 'medium'
            else:
                # Long term
                if availability_percent < 10:
                    return 'high'
                else:
                    return 'low'
        
        except Exception as e:
            logger.error(f"Error calculating demand: {str(e)}")
            return 'medium'
    
    def calculate_dynamic_price(self, ticket, base_price):
        """Calculate dynamic price based on demand"""
        try:
            demand = self.get_demand_level(ticket)
            
            # Price multipliers based on demand
            multipliers = {
                'very_high': Decimal('1.50'),  # 50% increase
                'high': Decimal('1.25'),       # 25% increase
                'medium': Decimal('1.00'),     # No change
                'low': Decimal('0.85')         # 15% decrease
            }
            
            multiplier = multipliers.get(demand, Decimal('1.00'))
            new_price = base_price * multiplier
            
            return new_price, demand
        
        except Exception as e:
            logger.error(f"Error calculating dynamic price: {str(e)}")
            return base_price, 'medium'
    
    def apply_bulk_discount(self, ticket, quantity):
        """Apply bulk discount for multiple tickets"""
        try:
            if quantity >= 100:
                return Decimal('0.80')  # 20% discount
            elif quantity >= 50:
                return Decimal('0.85')  # 15% discount
            elif quantity >= 20:
                return Decimal('0.90')  # 10% discount
            elif quantity >= 10:
                return Decimal('0.95')  # 5% discount
            else:
                return Decimal('1.00')  # No discount
        
        except Exception as e:
            logger.error(f"Error applying bulk discount: {str(e)}")
            return Decimal('1.00')
    
    def apply_early_bird_discount(self, ticket):
        """Apply early bird discount for events far in the future"""
        try:
            if not ticket.event:
                return Decimal('1.00')
            
            days_until = (ticket.event.date - timezone.now()).days
            
            if days_until > 90:
                return Decimal('0.85')  # 15% discount
            elif days_until > 60:
                return Decimal('0.90')  # 10% discount
            elif days_until > 30:
                return Decimal('0.95')  # 5% discount
            else:
                return Decimal('1.00')  # No discount
        
        except Exception as e:
            logger.error(f"Error applying early bird discount: {str(e)}")
            return Decimal('1.00')
    
    def apply_category_pricing(self, ticket):
        """Apply category-based pricing adjustments"""
        try:
            if not ticket.event or not ticket.event.category:
                return Decimal('1.00')
            
            category_multipliers = {
                'Football': Decimal('1.15'),
                'Formula 1': Decimal('1.30'),
                'Tennis': Decimal('1.10'),
                'Music': Decimal('1.05'),
                'Other': Decimal('1.00')
            }
            
            category_name = ticket.event.category.name
            return category_multipliers.get(category_name, Decimal('1.00'))
        
        except Exception as e:
            logger.error(f"Error applying category pricing: {str(e)}")
            return Decimal('1.00')
    
    def update_ticket_price(self, ticket, strategy='dynamic'):
        """Update ticket price based on strategy"""
        try:
            if not ticket.sell_price:
                logger.warning(f"Ticket {ticket.ticket_id} has no base price")
                return False
            
            base_price = Decimal(str(ticket.sell_price))
            new_price = base_price
            
            if strategy == 'dynamic':
                # Apply dynamic pricing
                new_price, demand = self.calculate_dynamic_price(ticket, base_price)
                
                # Apply early bird discount
                early_bird = self.apply_early_bird_discount(ticket)
                new_price = new_price * early_bird
                
                # Apply category pricing
                category = self.apply_category_pricing(ticket)
                new_price = new_price * category
                
                # Round to 2 decimal places
                new_price = new_price.quantize(Decimal('0.01'))
                
                # Store adjustment info
                adjustment = {
                    'ticket_id': ticket.ticket_id,
                    'old_price': float(base_price),
                    'new_price': float(new_price),
                    'demand': demand,
                    'strategy': strategy
                }
                self.price_adjustments.append(adjustment)
                
                # Update ticket price
                if new_price != base_price:
                    ticket.sell_price = new_price
                    ticket.save()
                    logger.info(f"✓ Updated {ticket.ticket_id}: £{base_price} → £{new_price} (Demand: {demand})")
                    self.updated_count += 1
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error updating ticket price: {str(e)}")
            self.error_count += 1
            traceback.print_exc()
            return False
    
    def optimize_section_pricing(self, section):
        """Optimize pricing for all tickets in a section"""
        try:
            tickets = Ticket.objects.filter(section=section)
            
            for ticket in tickets:
                self.update_ticket_price(ticket, strategy='dynamic')
            
            logger.info(f"✓ Optimized pricing for section: {section.name}")
        
        except Exception as e:
            logger.error(f"Error optimizing section pricing: {str(e)}")
            self.error_count += 1
    
    def optimize_event_pricing(self, event):
        """Optimize pricing for all tickets in an event"""
        try:
            sections = Section.objects.filter(event=event)
            
            for section in sections:
                self.optimize_section_pricing(section)
            
            logger.info(f"✓ Optimized pricing for event: {event.name}")
        
        except Exception as e:
            logger.error(f"Error optimizing event pricing: {str(e)}")
            self.error_count += 1
    
    def run(self):
        """Run pricing optimization"""
        try:
            logger.info("=" * 60)
            logger.info("Starting Pricing Optimization")
            logger.info("=" * 60)
            
            # Get all active events
            active_events = Event.objects.filter(
                is_active=True,
                date__gte=timezone.now()
            )
            
            if not active_events.exists():
                logger.info("No active events found for pricing optimization")
                return
            
            logger.info(f"Found {active_events.count()} active events")
            
            # Optimize pricing for each event
            for event in active_events:
                self.optimize_event_pricing(event)
            
            # Generate summary
            logger.info("=" * 60)
            logger.info("Pricing Optimization Complete")
            logger.info(f"✓ Updated: {self.updated_count} tickets")
            logger.info(f"✗ Errors: {self.error_count}")
            logger.info("=" * 60)
            
            # Log price adjustments
            if self.price_adjustments:
                logger.info("\nPrice Adjustments Summary:")
                total_adjustment = 0
                for adj in self.price_adjustments[:10]:  # Show first 10
                    change = adj['new_price'] - adj['old_price']
                    total_adjustment += change
                    logger.info(f"  {adj['ticket_id']}: £{adj['old_price']:.2f} → £{adj['new_price']:.2f} ({adj['demand']})")
                
                if len(self.price_adjustments) > 10:
                    logger.info(f"  ... and {len(self.price_adjustments) - 10} more")
                
                logger.info(f"\nTotal Revenue Impact: £{total_adjustment:.2f}")
        
        except Exception as e:
            logger.error(f"Fatal error in pricing optimization: {str(e)}")
            traceback.print_exc()


def main():
    """Main entry point"""
    try:
        manager = PricingManager()
        manager.run()
    except Exception as e:
        logger.error(f"Failed to run pricing manager: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
