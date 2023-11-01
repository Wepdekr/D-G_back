from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework import exceptions
from server import models
from django.http import JsonResponse
import random
import base64


def md5(user):
    import hashlib
    import time
    ctime = str(time.time())
    m = hashlib.md5(bytes(user, encoding='utf-8'))
    m.update(bytes(ctime, encoding='utf-8'))
    return m.hexdigest()


class Authtication(object):

    def authenticate(self, request):
        token = request.data.get('token')
        token_obj = models.User_Info.objects.filter(token=token).first()
        if not token_obj:
            raise exceptions.AuthenticationFailed('token失效')
        return token_obj, token

    def authenticate_header(self, request):
        pass


class Register(APIView):

    def post(self, request):
        ret = {}
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            ret['status_code'] = 404
            ret['msg'] = '请求参数错误'
            return JsonResponse(ret)
        user = models.User_Info.objects.filter(username=username).first()
        if user:
            ret['status_code'] = 404
            ret['msg'] = '用户已注册'
            return JsonResponse(ret)
        models.User_Info.objects.create(username=username, password=password)
        ret['status_code'] = 200
        ret['msg'] = '注册成功'
        return JsonResponse(ret)


class Login(APIView):

    def post(self, request):
        ret = {}
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            ret['status_code'] = 404
            ret['msg'] = '请求参数错误'
            return JsonResponse(ret)
        user = models.User_Info.objects.filter(username=username, password=password).first()
        if not user:
            ret['status_code'] = 404
            ret['msg'] = '用户名或密码错误'
            return JsonResponse(ret)
        token = md5(username)
        user.token = token
        user.save()
        ret['status_code'] = 200
        ret['token'] = token
        ret['msg'] = '登录成功'
        return JsonResponse(ret)


class Room(APIView):
    authentication_classes = [Authtication, ]

    def get(self, request):
        ret = {}
        room_id = request.GET.get('room_id')
        room = models.Room_Info.objects.filter(room_id=room_id).first()
        if not room:
            ret['status_code'] = 404
            ret['msg'] = '房间不存在'
            return JsonResponse(ret)
        ret['state'] = room.state
        ret['lexicon_id'] = room.lexicon_id
        ret['member'] = room.member
        ret['ready'] = room.ready
        ret['owner'] = room.owner
        return JsonResponse(ret)

    def post(self, request):
        ret = {}
        owner = request.user
        room_id = ''
        for _ in range(8):
            room_id += chr(random.randint(97, 122))
        models.Room_Info.objects.create(room_id=room_id, owner=owner.username, member=owner.username, ready='1')
        ret['status_code'] = 200
        ret['room_id'] = room_id
        ret['msg'] = '创建成功'
        return JsonResponse(ret)

class Join(APIView):
    authentication_classes = [Authtication, ]

    def post(self, request):
        ret = {}
        user = request.user
        room_id = request.POST.get('room_id')
        room = models.Room_Info.objects.filter(room_id=room_id).first()
        room.member = room.member + ',' + user.username
        room.ready = room.ready + ',' + '0'
        ret['status_code'] = 200
        ret['msg'] = '加入成功'
        return JsonResponse(ret)

class Start(APIView):
    authentication_classes = [Authtication, ]

    def post(self, request):
        ret = {}
        user = request.user
        room_id = request.POST.get('room_id')
        room = models.Room_Info.objects.filter(room_id=room_id).first()
        member = room.member.split(',')
        ready = room.ready.split(',')
        if user.username not in member:
            ret['status_code'] = 404
            ret['msg'] = '未在房间中'
            return JsonResponse(ret)
        if member[0] == user.username:
            if 0 in ready:
                ret['status_code'] = 200
                ret['msg'] = '有人未准备'
            else:
                room.state = 1
                room.save()
                ret['status_code'] = 200
                ret['msg'] = '开始'
            return JsonResponse(ret)
        else:
            pos = 0
            for i in range(len(member)):
                if user.username == member[i]:
                    pos = i
                    break
            if ready[pos] == 0:
                ready[pos] = 1
                ret['status_code'] = 200
                ret['msg'] = '准备'
            else:
                ready[pos] = 0
                ret['status_code'] = 200
                ret['msg'] = '取消准备'
            ready_text = ready[0]
            for i in range(1,(len(ready))):
                ready_text = ready_text + ',' + ready[i]
            room.ready = ready_text
            room.save()
        return JsonResponse(ret)