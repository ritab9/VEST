# Generated by Django 4.0 on 2023-01-06 00:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_profile_updated_at_student_updated_at'),
        ('emailing', '0008_alter_defaultmessage_subject_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='overridemessage',
            unique_together={('name', 'school')},
        ),
    ]
