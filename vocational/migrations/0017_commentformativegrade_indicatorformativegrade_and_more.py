# Generated by Django 4.0 on 2022-02-04 15:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vocational', '0016_alter_ethicsgrade_date_submitted_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentFormativeGrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commendation', models.CharField(max_length=300)),
                ('recommendation', models.CharField(max_length=300)),
                ('comment', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='IndicatorFormativeGrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=3)),
            ],
        ),
        migrations.CreateModel(
            name='IndicatorSummativeGrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=3)),
                ('comment', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='ethicsgrade',
            name='commendation',
        ),
        migrations.RemoveField(
            model_name='ethicsgrade',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='ethicsgrade',
            name='recommendation',
        ),
        migrations.DeleteModel(
            name='IndicatorGrade',
        ),
        migrations.AddField(
            model_name='indicatorsummativegrade',
            name='grade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vocational.ethicsgrade'),
        ),
        migrations.AddField(
            model_name='indicatorsummativegrade',
            name='indicator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vocational.vocationalindicator'),
        ),
        migrations.AddField(
            model_name='indicatorformativegrade',
            name='grade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vocational.ethicsgrade'),
        ),
        migrations.AddField(
            model_name='indicatorformativegrade',
            name='indicator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vocational.vocationalindicator'),
        ),
        migrations.AddField(
            model_name='commentformativegrade',
            name='grade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vocational.ethicsgrade'),
        ),
    ]
