# Generated by Django 4.0 on 2022-10-25 23:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0064_alter_schoolsettings_school_year_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ethicsformativegrade',
            name='score',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='ethicssummativegrade',
            name='score',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)]),
        ),
    ]
