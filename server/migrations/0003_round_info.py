# Generated by Django 4.2.6 on 2023-11-16 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0002_work_info_approval_work_info_disapproval'),
    ]

    operations = [
        migrations.CreateModel(
            name='Round_info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_id', models.TextField(default='')),
                ('round', models.IntegerField(default=0)),
                ('round_state', models.IntegerField(default=-1)),
                ('submit_num', models.IntegerField(default=0)),
                ('submit_member', models.TextField(default='')),
                ('start_time', models.IntegerField(default=0)),
                ('ready_num', models.IntegerField(default=0)),
                ('ready_member', models.TextField(default='')),
            ],
        ),
    ]