# Generated by Django 4.0 on 2023-08-29 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0027_school_email_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='email_update',
            field=models.DateField(blank=True, null=True),
        ),
    ]
