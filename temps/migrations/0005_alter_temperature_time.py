# Generated by Django 4.2.15 on 2024-09-06 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('temps', '0004_alter_temperature_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='temperature',
            name='time',
            field=models.TextField(),
        ),
    ]
