# Generated migration for EventCategory model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_category_country_category_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('icon', models.CharField(blank=True, max_length=50, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Event Categories',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.AddField(
            model_name='event',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='events', to='events.eventcategory'),
        ),
        migrations.AddField(
            model_name='event',
            name='category_legacy',
            field=models.CharField(blank=True, choices=[('concert', 'Concert'), ('sports', 'Sports'), ('theater', 'Theater'), ('conference', 'Conference'), ('festival', 'Festival'), ('other', 'Other')], max_length=20, null=True),
        ),
    ]
