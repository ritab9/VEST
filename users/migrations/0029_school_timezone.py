# Generated by Django 5.1 on 2024-08-21 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0028_alter_school_email_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='timezone',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
