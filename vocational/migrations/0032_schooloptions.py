# Generated by Django 4.0 on 2022-06-17 09:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_remove_student_active'),
        ('vocational', '0031_studentassignment_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolOptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timebased', models.CharField(choices=[('N', 'None'), ('H', 'Hours'), ('D', 'Days'), ('W', 'Weeks')], default='N', max_length=1)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.school')),
            ],
        ),
    ]