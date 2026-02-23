#!/usr/bin/env python
"""
Script to run migrations and populate categories on startup
This helps with Railway deployments
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'go2events.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.db.utils import OperationalError

def run_migrations():
    """Run all pending migrations"""
    try:
        print("Running migrations...")
        call_command('migrate', verbosity=2)
        print("✓ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"✗ Migration error: {str(e)}")
        return False

def populate_categories():
    """Populate event categories"""
    try:
        print("Populating categories...")
        call_command('populate_categories', verbosity=2)
        print("✓ Categories populated successfully")
        return True
    except Exception as e:
        print(f"✗ Category population error: {str(e)}")
        return False

def check_database():
    """Check if database is accessible"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Database connection successful")
        return True
    except OperationalError as e:
        print(f"✗ Database connection failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Go2Events - Startup Migration Script")
    print("=" * 60)
    
    # Check database
    if not check_database():
        print("Cannot proceed without database connection")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        print("Migrations failed, but continuing...")
    
    # Populate categories
    if not populate_categories():
        print("Category population failed, but continuing...")
    
    print("=" * 60)
    print("Startup tasks completed")
    print("=" * 60)
