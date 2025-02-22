# Generated by Django 3.0.8 on 2021-04-09 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_merchantrequest_isprocessed'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShadepayRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wallet', models.CharField(max_length=255)),
                ('amount', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=255)),
                ('isProcessed', models.BooleanField(default=False)),
                ('approved', models.BooleanField(default=False)),
                ('returnUrl', models.URLField()),
                ('date', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
