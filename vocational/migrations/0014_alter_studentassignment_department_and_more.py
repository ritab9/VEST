# Generated by Django 4.0 on 2022-01-28 17:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0013_studentassignment_instructorassignment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentassignment',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vocational.department'),
        ),
        migrations.AlterUniqueTogether(
            name='studentassignment',
            unique_together={('quarter', 'department')},
        ),
    ]
