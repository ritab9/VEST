# Generated by Django 4.0 on 2022-12-12 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_remove_student_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='school',
            name='foundation',
        ),
        migrations.AddField(
            model_name='school',
            name='email_address',
            field=models.EmailField(default='', max_length=254),
        ),
    ]