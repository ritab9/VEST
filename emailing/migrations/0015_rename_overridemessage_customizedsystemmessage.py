# Generated by Django 4.0 on 2023-02-02 18:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_profile_updated_at_student_updated_at'),
        ('emailing', '0014_rename_defaultmessage_systemmessage'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OverrideMessage',
            new_name='CustomizedSystemMessage',
        ),
    ]
