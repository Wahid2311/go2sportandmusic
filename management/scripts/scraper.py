#!/usr/bin/env python3
"""
Web Scraper Script
Scrapes events from external sources and imports them into the database
"""

import os
import sys
import django
import traceback
import logging
import requests
from datetime import datetime
from pathlib import Path
import multiprocessing
import time

# Setup Django
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'go2events.settings')
django.setup()

from events.models import Event, Category
from django.utils import timezone

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EventScraper:
    """Base scraper class for events"""
    
    def __init__(self):
        self.scraped_events = []
        self.error_count = 0
    
    def fetch_events(self):
        """Override in subclass"""
        raise NotImplementedError
    
    def parse_events(self, data):
        """Override in subclass"""
        raise NotImplementedError
    
    def save_events(self):
        """Save scraped events to database"""
        try:
            for event_data in self.scraped_events:
                try:
                    # Check if event already exists
                    existing = Event.objects.filter(
                        external_id=event_data.get('external_id')
                    ).first()
                    
                    if existing:
                        logger.info(f"Event already exists: {event_data['name']}")
                        continue
                    
                    # Get or create category
                    category_name = event_data.get('category', 'Other')
                    category, _ = Category.objects.get_or_create(name=category_name)
                    
                    # Create event
                    event = Event.objects.create(
                        name=event_data['name'],
                        description=event_data.get('description', ''),
                        date=event_data['date'],
                        location=event_data.get('location', ''),
                        category=category,
                        external_id=event_data.get('external_id'),
                        image_url=event_data.get('image_url', ''),
                        is_active=True
                    )
                    
                    logger.info(f"✓ Created event: {event.name} on {event.date}")
                    
                except Exception as e:
                    logger.error(f"✗ Error saving event: {str(e)}")
                    self.error_count += 1
                    traceback.print_exc()
        
        except Exception as e:
            logger.error(f"Fatal error saving events: {str(e)}")
            traceback.print_exc()
    
    def run(self):
        """Run the scraper"""
        try:
            logger.info(f"Starting {self.__class__.__name__}")
            self.fetch_events()
            self.parse_events(None)
            self.save_events()
            logger.info(f"Completed {self.__class__.__name__}")
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {str(e)}")
            traceback.print_exc()


class XS2EventsScraper(EventScraper):
    """Scraper for XS2Events API"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('XS2EVENT_API_KEY')
        self.base_url = 'https://api.xs2events.com/v1'
    
    def fetch_events(self):
        """Fetch events from XS2Events API"""
        try:
            if not self.api_key:
                logger.error("XS2EVENT_API_KEY not set in environment")
                return
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Fetch events from API
            response = requests.get(
                f'{self.base_url}/events',
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            self.parse_events(data)
            
            logger.info(f"✓ Fetched {len(self.scraped_events)} events from XS2Events")
            
        except requests.RequestException as e:
            logger.error(f"✗ Error fetching from XS2Events: {str(e)}")
            self.error_count += 1
        except Exception as e:
            logger.error(f"✗ Unexpected error: {str(e)}")
            traceback.print_exc()
            self.error_count += 1
    
    def parse_events(self, data):
        """Parse events from API response"""
        try:
            if not data or 'events' not in data:
                logger.warning("No events found in API response")
                return
            
            for event in data['events']:
                try:
                    event_data = {
                        'name': event.get('name'),
                        'description': event.get('description'),
                        'date': datetime.fromisoformat(event.get('date')),
                        'location': event.get('venue', {}).get('name', ''),
                        'category': event.get('category'),
                        'external_id': f"xs2_{event.get('id')}",
                        'image_url': event.get('image_url', '')
                    }
                    self.scraped_events.append(event_data)
                except Exception as e:
                    logger.error(f"Error parsing event: {str(e)}")
                    self.error_count += 1
        
        except Exception as e:
            logger.error(f"Error parsing events: {str(e)}")
            traceback.print_exc()


class TicketmasterScraper(EventScraper):
    """Scraper for Ticketmaster API"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('TICKETMASTER_API_KEY')
        self.base_url = 'https://app.ticketmaster.com/discovery/v2'
    
    def fetch_events(self):
        """Fetch events from Ticketmaster API"""
        try:
            if not self.api_key:
                logger.error("TICKETMASTER_API_KEY not set in environment")
                return
            
            params = {
                'apikey': self.api_key,
                'countryCode': 'GB',
                'size': 200
            }
            
            response = requests.get(
                f'{self.base_url}/events',
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            self.parse_events(data)
            
            logger.info(f"✓ Fetched {len(self.scraped_events)} events from Ticketmaster")
            
        except requests.RequestException as e:
            logger.error(f"✗ Error fetching from Ticketmaster: {str(e)}")
            self.error_count += 1
        except Exception as e:
            logger.error(f"✗ Unexpected error: {str(e)}")
            traceback.print_exc()
            self.error_count += 1
    
    def parse_events(self, data):
        """Parse events from API response"""
        try:
            if '_embedded' not in data or 'events' not in data['_embedded']:
                logger.warning("No events found in Ticketmaster response")
                return
            
            for event in data['_embedded']['events']:
                try:
                    event_data = {
                        'name': event.get('name'),
                        'description': event.get('description', ''),
                        'date': datetime.fromisoformat(event['dates']['start']['dateTime'].replace('Z', '+00:00')),
                        'location': event['_embedded']['venues'][0].get('name', '') if '_embedded' in event else '',
                        'category': event['classifications'][0].get('segment', {}).get('name', 'Other') if event.get('classifications') else 'Other',
                        'external_id': f"tm_{event.get('id')}",
                        'image_url': event['images'][0]['url'] if event.get('images') else ''
                    }
                    self.scraped_events.append(event_data)
                except Exception as e:
                    logger.error(f"Error parsing event: {str(e)}")
                    self.error_count += 1
        
        except Exception as e:
            logger.error(f"Error parsing events: {str(e)}")
            traceback.print_exc()


def run_xs2events_scraper():
    """Run XS2Events scraper in separate process"""
    try:
        scraper = XS2EventsScraper()
        scraper.run()
    except Exception as e:
        logger.error(f"Error in XS2Events scraper: {str(e)}")
        traceback.print_exc()


def run_ticketmaster_scraper():
    """Run Ticketmaster scraper in separate process"""
    try:
        scraper = TicketmasterScraper()
        scraper.run()
    except Exception as e:
        logger.error(f"Error in Ticketmaster scraper: {str(e)}")
        traceback.print_exc()


def main():
    """Main entry point with multiprocessing"""
    try:
        logger.info("=" * 60)
        logger.info("Starting Web Scraper")
        logger.info("=" * 60)
        
        processes = []
        
        # Start XS2Events scraper
        xs_process = multiprocessing.Process(
            name='XS2EventsScraper',
            target=run_xs2events_scraper
        )
        processes.append(xs_process)
        xs_process.start()
        time.sleep(2)
        
        # Start Ticketmaster scraper
        tm_process = multiprocessing.Process(
            name='TicketmasterScraper',
            target=run_ticketmaster_scraper
        )
        processes.append(tm_process)
        tm_process.start()
        
        # Wait for all processes to complete
        for process in processes:
            process.join()
        
        logger.info("=" * 60)
        logger.info("Web Scraper Complete")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Failed to run scraper: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
