# Generated by Django 4.0 on 2022-06-17 09:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0032_schooloptions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentassignment',
            name='time',
        ),
    ]
