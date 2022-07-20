# Generated by Django 4.0 on 2022-06-06 11:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_alter_student_graduation_year'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vocational', '0023_alter_indicatorformativegrade_value'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='indicatorsummativegrade',
            options={'ordering': ('id',)},
        ),
        migrations.CreateModel(
            name='VocationalAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vocational.department')),
                ('instructor', models.ManyToManyField(blank=True, related_name='i_assignments', to=settings.AUTH_USER_MODEL)),
                ('quarter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vocational.quarter')),
                ('student', models.ManyToManyField(blank=True, related_name='s_assignment', to='users.Student')),
            ],
            options={
                'unique_together': {('quarter', 'department')},
            },
        ),
    ]
