# Generated by Django 3.0.8 on 2021-02-27 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20210217_0650'),
    ]

    operations = [
        migrations.RenameField(
            model_name='additionalinformation',
            old_name='BVN',
            new_name='nin',
        ),
        migrations.RemoveField(
            model_name='additionalinformation',
            name='DOB',
        ),
        migrations.AddField(
            model_name='additionalinformation',
            name='accepted_terms',
            field=models.BooleanField(default=True),
        ),
    ]
