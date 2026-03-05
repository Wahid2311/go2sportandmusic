# Generated migration to add Stripe fields without ArrayField changes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0006_populate_ticket_numbers'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='stripe_payment_intent_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='stripe_session_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='bundle_id',
            field=models.UUIDField(blank=True, db_index=True, help_text='Groups tickets that must be sold together', null=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='sell_together',
            field=models.BooleanField(default=False, help_text='If checked, all tickets in this bundle must be purchased together'),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.CharField(blank=True, db_index=True, help_text='Custom order number for display (e.g., Order# 286884113)', max_length=20, null=True, unique=True),
        ),
        migrations.CreateModel(
            name='TicketReservation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity_reserved', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('is_expired', models.BooleanField(db_index=True, default=False)),
                ('buyer', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='reservations', to='auth.user')),
                ('order', models.OneToOneField(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='reservation', to='tickets.order')),
                ('ticket', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='reservations', to='tickets.ticket')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
