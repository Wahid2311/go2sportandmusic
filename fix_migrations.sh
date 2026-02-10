#!/bin/bash

# Script to fix broken migrations before running Django migrations

echo "Fixing broken migrations..."

# Use sqlite3 to directly delete the broken migration records
if [ -f "db.sqlite3" ]; then
    sqlite3 db.sqlite3 << EOF
DELETE FROM django_migrations 
WHERE app = 'events' AND name IN (
    '0009_fix_null_categories',
    '0010_allow_null_category',
    '0011_remove_category_constraint',
    '0012_fix_database_schema',
    '0013_add_timestamps_to_eventcategory',
    '0014_fix_eventcategory_schema',
    '0015_safe_eventcategory_fix',
    '0016_reset_and_fix_migrations',
    '0017_final_eventcategory_fix',
    '0018_mark_failed_migrations_unapplied',
    '0019_ultimate_fix'
);
EOF
    echo "Cleaned up broken migration records"
else
    echo "Database file not found, skipping cleanup"
fi

# Now run the normal migrate command
echo "Running migrations..."
python manage.py migrate

echo "Migrations completed"
