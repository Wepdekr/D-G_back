# Generated by Django 4.2.6 on 2023-11-03 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='work_info',
            name='approval',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='work_info',
            name='disapproval',
            field=models.IntegerField(default=0),
        ),
    ]
