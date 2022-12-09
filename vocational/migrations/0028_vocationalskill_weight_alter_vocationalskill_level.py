# Generated by Django 4.0 on 2022-06-16 12:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0027_skillvalue_number_alter_skillvalue_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='vocationalskill',
            name='weight',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=4),
        ),
        migrations.AlterField(
            model_name='vocationalskill',
            name='level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vocational.ethicslevel'),
        ),
    ]