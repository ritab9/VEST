# Generated by Django 4.0 on 2022-12-16 15:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emailing', '0005_rename_default_email_message_defaultmessage_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='defaultmessage',
            old_name='default_message',
            new_name='message',
        ),
        migrations.RenameField(
            model_name='overridemessage',
            old_name='new_message',
            new_name='message',
        ),
    ]
