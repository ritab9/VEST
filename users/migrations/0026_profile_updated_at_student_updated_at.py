# Generated by Django 4.0 on 2022-12-28 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_school_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='student',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
