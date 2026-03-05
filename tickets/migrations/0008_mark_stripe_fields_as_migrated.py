# This migration marks the Stripe fields as already migrated
# The columns already exist in the production database from previous migration attempts
# This migration is a no-op to sync the migration state

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0006_populate_ticket_numbers'),
    ]

    operations = [
        # No operations needed - columns already exist in production database
        # This migration just marks the state as correct
    ]
