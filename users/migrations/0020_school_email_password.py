# Generated by Django 4.0 on 2022-12-12 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_remove_school_foundation_school_email_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='email_password',
            field=models.CharField(default='', max_length=50),
        ),
    ]
