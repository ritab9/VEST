# Generated by Django 4.0 on 2022-01-31 15:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_alter_student_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='graduation_year',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(2020), django.core.validators.MaxValueValidator(2100)]),
        ),
    ]
