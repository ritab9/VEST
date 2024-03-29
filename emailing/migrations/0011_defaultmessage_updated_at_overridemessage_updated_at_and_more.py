# Generated by Django 4.0 on 2023-01-10 21:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('emailing', '0010_alter_overridemessage_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='defaultmessage',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='overridemessage',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='schoolmessage',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='overridemessage',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='overridden', to='emailing.defaultmessage'),
        ),
    ]
