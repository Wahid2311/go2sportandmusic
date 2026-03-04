#!/usr/bin/env python
"""
Startup script to run migrations and generate custom IDs automatically
This should be called before starting the Django application
"""

import os
import sys
import django
from django.core.management import call_command

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'go2events.settings')
django.setup()

def run_startup_tasks():
    """Run all startup tasks"""
    print("=" * 60)
    print("🚀 Running TicketHouse Startup Tasks...")
    print("=" * 60)
    
    try:
        # Step 1: Run migrations
        print("\n📦 Step 1: Running database migrations...")
        call_command('migrate', verbosity=2)
        print("✓ Migrations completed successfully!")
        
        # Step 2: Generate custom IDs for existing data
        print("\n🔢 Step 2: Generating custom IDs for existing tickets and orders...")
        call_command('generate_custom_ids', verbosity=2)
        print("✓ Custom ID generation completed successfully!")
        
        print("\n" + "=" * 60)
        print("✅ All startup tasks completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during startup tasks: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    run_startup_tasks()
