# Generated by Django 5.1 on 2025-05-15 06:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0090_alter_ethicsgraderecord_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vocationalstatus',
            name='vocational_class',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vocational.vocationalclass'),
        ),
    ]
