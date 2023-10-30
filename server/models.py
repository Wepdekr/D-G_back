from django.db import models

# Create your models here.
class User_Info(models.Model):  # 用户信息
    username = models.TextField(default='')
    password = models.TextField(max_length=32, default='')
    token = models.TextField(max_length=64,default='')

class Room_Info(models.Model):
    owner = models.TextField(default='')
    lexicon_id = models.IntegerField(default=0)
    state = models.BooleanField(default=False)
    member = models.TextField(default='')
    ready = models.TextField(default='')