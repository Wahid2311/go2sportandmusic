from django.db import migrations, models
from django.contrib.postgres.fields import ArrayField


def alter_seats_field(apps, schema_editor):
    """Alter the seats field based on database backend"""
    connection = schema_editor.connection
    
    if connection.vendor == 'postgresql':
        # For PostgreSQL, use ArrayField
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE tickets_ticket
                ALTER COLUMN seats TYPE text[] USING CASE 
                    WHEN seats IS NULL THEN NULL
                    ELSE string_to_array(seats, ',')
                END,
                ALTER COLUMN seats SET DEFAULT ARRAY[]::text[]
            """)
    else:
        # For SQLite and others, keep as TextField
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            code=alter_seats_field,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
