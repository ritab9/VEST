# Generated by Django 4.0 on 2022-07-28 14:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0053_ethicsgraderecord_student_discussion_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='grademessages',
            old_name='grade',
            new_name='grade_record',
        ),
    ]
