# Generated by Django 5.1.6 on 2025-03-05 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_plan_subscription'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='start_date',
        ),
        migrations.AddField(
            model_name='plan',
            name='stripe_price_id',
            field=models.CharField(default='default_price_id', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='plan',
            name='ad_variations_per_month',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='plan',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='plan',
            name='price_per_month',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('canceled', 'Canceled')], default='active', max_length=20),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='stripe_subscription_id',
            field=models.CharField(default='default_subscription_id', max_length=100, unique=True),
        ),
    ]
