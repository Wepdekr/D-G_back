from django.db import models

# Create your models here.
class User_Info(models.Model):  # 用户信息
    username = models.TextField(default='')
    password = models.TextField(max_length=32, default='')
    token = models.TextField(max_length=64,default='')

class Room_Info(models.Model):
    room_id = models.TextField(default='')
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
    category = models.IntegerField(default=0)  # 0图片 1词语
    img = models.TextField(default='')
    word = models.TextField(default='')
    approval = models.IntegerField(default=0)
    disapproval = models.IntegerField(default=0)