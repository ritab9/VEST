# Generated by Django 5.1 on 2024-08-28 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0087_timecard_week_range'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timecard',
            name='week_range',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
