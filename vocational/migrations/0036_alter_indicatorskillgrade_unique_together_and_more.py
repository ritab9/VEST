# Generated by Django 4.0 on 2022-06-17 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0035_remove_skillvalue_grade_indicatorskillgrade'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='indicatorskillgrade',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='indicatorskillgrade',
            name='skill',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='vocational.vocationalskill'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='indicatorskillgrade',
            name='value',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='vocational.skillvalue'),
        ),
        migrations.AlterUniqueTogether(
            name='indicatorskillgrade',
            unique_together={('skill', 'grade')},
        ),
        migrations.RemoveField(
            model_name='indicatorskillgrade',
            name='indicator',
        ),
    ]
