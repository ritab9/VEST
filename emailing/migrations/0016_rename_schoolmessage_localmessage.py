# Generated by Django 4.0 on 2023-02-02 19:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_profile_updated_at_student_updated_at'),
        ('emailing', '0015_rename_overridemessage_customizedsystemmessage'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SchoolMessage',
            new_name='LocalMessage',
        ),
    ]
