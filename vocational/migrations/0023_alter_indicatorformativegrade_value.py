# Generated by Django 4.0 on 2022-05-23 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0022_ethicsgrade_commendation_ethicsgrade_recommendation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicatorformativegrade',
            name='value',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True),
        ),
    ]
