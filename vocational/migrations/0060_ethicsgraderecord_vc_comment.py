# Generated by Django 4.0 on 2022-10-06 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0059_alter_ethicsgraderecord_student_discussed'),
    ]

    operations = [
        migrations.AddField(
            model_name='ethicsgraderecord',
            name='vc_comment',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
