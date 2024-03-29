# Generated by Django 4.0 on 2022-01-21 21:21

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0004_alter_vocationalstatus_student'),
    ]

    operations = [
        migrations.CreateModel(
            name='VocationalIndicator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('number', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vocational.vocationallevel')),
            ],
        ),
    ]
