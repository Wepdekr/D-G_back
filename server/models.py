from django.db import models

# Create your models here.
class User_Info(models.Model):  # 用户信息
    username = models.TextField(default='')  # TODO 用户名应当为unique
    password = models.TextField(max_length=32, default='')
    token = models.TextField(max_length=64,default='') # TODO token机制存在问题

class Room_Info(models.Model):
    room_id = models.TextField(default='') # TODO room_id应当为unique
    owner = models.TextField(default='')
    lexicon_id = models.IntegerField(default=0)
    state = models.BooleanField(default=False)
    member = models.TextField(default='')
    ready = models.TextField(default='')
    round = models.IntegerField(default=0)

class Work_info(models.Model):
    room_id = models.TextField(default='')
    round = models.IntegerField(default=0)
    username = models.TextField(default='')
    category = models.IntegerField(default=0)  #题目是？ 0图片 1词语
    img = models.TextField(default='')
    word = models.TextField(default='')

class Round_info(models.Model):
    room_id = models.TextField(default='')
    round = models.IntegerField(default=0)
    round_state = models.IntegerField(default=-1)
    submit_num = models.IntegerField(default=0)
    submit_member = models.TextField(default='')
    start_time = models.IntegerField(default=0)
    ready_num = models.IntegerField(default=0)
    ready_member = models.TextField(default='')

class Question_Vote(models.Model):
    room_id = models.TextField(default='')
    answer_seq = models.TextField(default='')
    show_pos = models.IntegerField(default=-1)
    show_time = models.IntegerField(default=0)
    finish_show = models.IntegerField(default=0)
    approval = models.IntegerField(default=0)
    disapproval = models.IntegerField(default=0)
    vote_member = models.TextField(default='')
    vote_num = models.IntegerField(default=0)