# Generated by Django 4.0 on 2022-07-27 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0046_alter_ethicsgraderecord_unique_together'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ethicsformativegrade',
            options={'ordering': ('id',)},
        ),
    ]
