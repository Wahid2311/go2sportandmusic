#!/bin/bash
# Script to clean up broken migrations from the database

DB_FILE="${DATABASE_URL#sqlite:///}"
if [ -z "$DB_FILE" ] || [ "$DB_FILE" = "$DATABASE_URL" ]; then
    # If DATABASE_URL is not set or doesn't start with sqlite:///, try default
    DB_FILE="db.sqlite3"
fi

echo "Database file: $DB_FILE"

if [ -f "$DB_FILE" ]; then
    echo "Cleaning up broken migrations..."
    
    # Delete all 0009+ migrations from events app
    sqlite3 "$DB_FILE" << EOF
DELETE FROM django_migrations WHERE app = 'events' AND (
    name LIKE '0009_%' OR 
    name LIKE '0010_%' OR 
    name LIKE '0011_%' OR 
    name LIKE '0012_%' OR 
    name LIKE '0013_%' OR 
    name LIKE '0014_%' OR 
    name LIKE '0015_%' OR 
    name LIKE '0016_%' OR 
    name LIKE '0017_%' OR 
    name LIKE '0018_%' OR 
    name LIKE '0019_%'
);
EOF
    
    echo "Migration cleanup completed!"
else
    echo "Database file not found: $DB_FILE"
fi
