# Generated by Django 4.0 on 2022-11-03 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0069_alter_schoolyear_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schoolyear',
            name='name',
            field=models.CharField(max_length=9, verbose_name='School Year (ex:2024-2025)'),
        ),
    ]