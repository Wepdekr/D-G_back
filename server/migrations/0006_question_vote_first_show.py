# Generated by Django 4.2.6 on 2023-11-17 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0005_question_vote_finish_show_question_vote_show_pos_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question_vote',
            name='first_show',
            field=models.IntegerField(default=1),
        ),
    ]
