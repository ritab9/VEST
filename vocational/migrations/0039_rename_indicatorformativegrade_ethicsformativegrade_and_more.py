# Generated by Django 4.0 on 2022-07-20 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0038_rename_ethicsindicator_ethicsdefinition_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='IndicatorFormativeGrade',
            new_name='EthicsFormativeGrade',
        ),
        migrations.RenameModel(
            old_name='IndicatorSummativeGrade',
            new_name='EthicsSummativeGrade',
        ),
    ]