from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework import exceptions
from server import models
from django.http import JsonResponse
import random
from random import sample
import json


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
            ret['status_code'] = 403
            ret['msg'] = '用户名重复，请更换用户名'
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
            ret['status_code'] = 403
            ret['msg'] = '用户名或密码错误'
            return JsonResponse(ret)
        token = md5(username) # TODO Token机制存在问题
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
        room.save()
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
            if '0' in ready:
                ret['status_code'] = 200
                ret['msg'] = '有人未准备'
            else:
                room.state = 1
                with open('server/lexicon.json', encoding='utf-8') as f:
                    lexicon_data = json.load(f)
                sort = ["动物类", "植物类", "食品类", "交通工具", "日常用品", "地点和建筑", "职业", "活动和娱乐"]
                lexicon = lexicon_data[sort[room.lexicon_id]]
                res = sample(lexicon, len(member))
                for i in range(len(res)):
                    models.Work_info.objects.create(username=member[i], room_id=room_id, round=0, category=1,
                                                    word=res[i])
                room.round = 1
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
            if ready[pos] == '0':
                ready[pos] = '1'
                ret['status_code'] = 200
                ret['msg'] = '准备'
            else:
                ready[pos] = '0'
                ret['status_code'] = 200
                ret['msg'] = '取消准备'
            ready_text = ready[0]
            for i in range(1, (len(ready))):
                ready_text = ready_text + ',' + ready[i]
            room.ready = ready_text
            room.save()
        return JsonResponse(ret)


class Lexicon(APIView):
    authentication_classes = [Authtication, ]

    def post(self, request):
        ret = {}
        room_id = request.POST.get('room_id')
        lexicon_id = request.POST.get('lexicon_id')
        user = request.user
        room = models.Room_Info.objects.filter(room_id=room_id).first()
        if user.username != room.owner:
            ret['status_code'] = 403
            ret['msg'] = '无修改权限'
        else:
            room.lexicon_id = lexicon_id
            room.save()
            ret['status_code'] = 200
            ret['msg'] = '修改成功'
        return JsonResponse(ret)


class Work(APIView):
    authentication_classes = [Authtication, ]

    def get(self, request):
        ret = {}
        room_id = request.GET.get('room_id')
        round = request.GET.get('round')
        username = request.GET.get('username')
        work = models.Work_info.objects.filter(room_id=room_id, round=round, username=username).first()
        if not work:
            ret['status_code'] = 404
            ret['msg'] = '参数错误'
            return JsonResponse(ret)
        if work.category == 1:
            ret['status_code'] = 200
            ret['word'] = work.word
            ret['img'] = ''
        else:
            ret['status_code'] = 200
            ret['word'] = ''
            ret['img'] = work.img
        return JsonResponse(ret)


class Submit(APIView):
    authentication_classes = [Authtication, ]

    def post(self, request):
        ret = {}
        user = request.user
        room_id = request.POST.get('room_id')
        is_word = request.POST.get('is_word')
        round = request.POST.get('round')
        if is_word == '1':
            word = request.POST.get('word')
            models.Work_info.objects.create(room_id=room_id, round=round, username=user.username, category=1, word=word)
        else:
            img = request.POST.get('img')
            models.Work_info.objects.create(room_id=room_id, round=round, username=user.username, category=0, img=img)
        room = models.Room_Info.objects.filter(room_id=room_id).first()
        if len(models.Work_info.objects.filter(room_id=room_id, round=round)) == len(room.member.split(',')):
            room.round = room.round + 1
            room.save()
        ret['status_code'] = 200
        ret['msg'] = '提交成功'
        return JsonResponse(ret)


class Round(APIView):
    authentication_classes = [Authtication, ]

    def get(self, request):
        ret = {}
        room_id = request.GET.get('room_id')
        room = models.Room_Info.objects.filter(room_id=room_id).first()
        if not room:
            ret['status_code'] = 404
            ret['msg'] = '房间号错误'
            return JsonResponse(ret)
        ret['status_code'] = 200
        ret['round'] = room.round
        return JsonResponse(ret)


class Vote(APIView):
    authentication_classes = [Authtication, ]

    def get(self, request):
        ret = {}
        room_id = request.GET.get('room_id')
        username = request.GET.get('username')
        round = request.GET.get('round')
        work = models.Work_info.objects.filter(room_id=room_id, username=username, round=round).first()
        if not work:
            ret['status_code'] = 404
            ret['msg'] = '未找到结果'
            return JsonResponse(ret)
        ret['status_code'] = 200
        ret['approval'] = work.approval
        ret['disapproval'] = work.disapproval
        return JsonResponse(ret)

    def post(self, request):
        ret = {}
        room_id = request.POST.get('room_id')
        username = request.POST.get('username')
        round = request.POST.get('round')
        result = request.POST.get('result')
        work = models.Work_info.objects.filter(room_id=room_id, username=username, round=round).first()
        if not work:
            ret['status_code'] = 404
            ret['msg'] = '未找到结果'
            return JsonResponse(ret)
        if result == '1':
            work.approval = work.approval + 1
        else:
            work.disapproval = work.disapproval + 1
        work.save()
        ret['status_code'] = 200
        return JsonResponse(ret)
