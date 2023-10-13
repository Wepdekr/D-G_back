from django.db import models

# Create your models here.
class User_Info(models.Model):  # 用户信息
    username = models.TextField(default='')
    password = models.TextField(max_length=32, default='')
    token = models.TextField(max_length=64,default='')