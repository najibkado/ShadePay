# Generated by Django 3.0.8 on 2021-03-02 09:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_developerinformation'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessPayattitudeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=255)),
                ('mobile', models.CharField(max_length=255)),
                ('is_successful', models.BooleanField(default=False)),
                ('status', models.CharField(max_length=255)),
                ('reference', models.CharField(max_length=255)),
                ('date', models.DateTimeField(auto_now=True)),
                ('business_wallet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payattitude_request_business_walet', to='main.BusinessWallet')),
                ('individual_wallet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payattitude_request_individual_walet', to='main.IndividualWallet')),
                ('saving_wallet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payattitude_request_saving_walet', to='main.SavingWallet')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payattitude_request', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
