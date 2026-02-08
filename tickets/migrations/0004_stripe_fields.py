# Generated migration for Stripe payment fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_ticket_bundle_id_ticket_sell_together'),
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
        migrations.AlterField(
            model_name='order',
            name='revolut_checkout_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='revolut_order_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
