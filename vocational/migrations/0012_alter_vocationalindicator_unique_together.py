# Generated by Django 4.0 on 2022-01-27 14:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0011_alter_department_options_schoolyear_active'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='vocationalindicator',
            unique_together={('name', 'level'), ('number', 'level')},
        ),
    ]