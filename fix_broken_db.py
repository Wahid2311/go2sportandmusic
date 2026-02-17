#!/usr/bin/env python
"""
Script to fix the broken database state before running migrations.
This script uses Django ORM to safely delete broken migration records.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'go2events.settings')
sys.path.insert(0, '/app')

try:
    django.setup()
    from django.db import connection
    from django.db.migrations.recorder import MigrationRecorder
    
    print("=" * 60)
    print("FIXING BROKEN DATABASE STATE")
    print("=" * 60)
    
    # Get the migration recorder
    recorder = MigrationRecorder(connection)
    
    # List of broken migrations to delete
    broken_migrations = [
        ('events', '0006_add_eventcategory_timestamps'),
        ('events', '0006_placeholder'),
        ('events', '0007_set_default_category'),
        ('events', '0009_fix_eventcategory_schema'),
        ('events', '0009_fix_null_categories'),
        ('events', '0009_verify_schema'),
        ('events', '0006_final_fix_all_issues'),
        ('tickets', '0002_alter_ticket_upload_file'),
        ('tickets', '0003_ticket_bundle_id_ticket_sell_together'),
        ('tickets', '0004_stripe_fields'),
        ('tickets', '0005_alter_ticket_upload_file'),
        ('tickets', '0006_recalculate_ticket_prices'),
    ]
    
    # Delete broken migrations
    deleted_count = 0
    for app, migration_name in broken_migrations:
        try:
            # Use the recorder to unapply the migration
            recorder.record_unapplied(app, migration_name)
            print(f"✓ Deleted migration record: {app}.{migration_name}")
            deleted_count += 1
        except Exception as e:
            # Try direct deletion if recorder method fails
            try:
                from django.db.migrations.models import Migration
                Migration.objects.filter(app=app, name=migration_name).delete()
                print(f"✓ Deleted migration record (direct): {app}.{migration_name}")
                deleted_count += 1
            except Exception as e2:
                print(f"⚠ Could not delete {app}.{migration_name}: {e2}")
    
    print(f"\n✓ Successfully deleted {deleted_count} broken migration records")
    print("=" * 60)
    
except Exception as e:
    print(f"✗ Error during database fix: {e}")
    import traceback
    traceback.print_exc()
    print("Continuing with migrations anyway...")
