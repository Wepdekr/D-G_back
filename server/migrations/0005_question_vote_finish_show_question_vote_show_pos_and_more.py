# Generated by Django 4.2.6 on 2023-11-17 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0004_question_vote_remove_work_info_approval_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question_vote',
            name='finish_show',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='question_vote',
            name='show_pos',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='question_vote',
            name='show_time',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='question_vote',
            name='vote_member',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='question_vote',
            name='vote_num',
            field=models.IntegerField(default=0),
        ),
    ]
