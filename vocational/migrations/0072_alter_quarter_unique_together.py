# Generated by Django 4.0 on 2022-12-20 23:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0071_rename_schoolsettings_gradesettings'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='quarter',
            unique_together={('school_year', 'name')},
        ),
    ]