#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'go2events.settings')
django.setup()

# Delete the database file to reset it completely
db_path = 'db.sqlite3'
if os.path.exists(db_path):
    print(f"Deleting database file: {db_path}")
    os.remove(db_path)
    print("Database file deleted successfully")
else:
    print(f"Database file not found at {db_path}")

print("Database reset complete. Django will recreate it with fresh migrations.")
