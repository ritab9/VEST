# Generated by Django 4.0 on 2022-12-12 17:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0019_remove_school_foundation_school_email_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='school_specific_email_message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, unique=True)),
                ('message', models.CharField(max_length=1800)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.school')),
            ],
        ),
        migrations.CreateModel(
            name='default_email_message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, unique=True)),
                ('default_message', models.CharField(max_length=1800)),
                ('override_message', models.CharField(max_length=1800)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.school')),
            ],
        ),
    ]
