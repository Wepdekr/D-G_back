from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework import exceptions
from server import models
from django.http import JsonResponse
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
        models.User_Info.objects.create(username=username, password=password, token=token)
        ret['status_code'] = 200
        ret['msg'] = '注册成功'
        return JsonResponse(ret)


class Login(APIView):

    def post(self, request):
        ret = {}
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            ret['code'] = 404
            ret['msg'] = '请求参数错误'
            return JsonResponse(ret)
        user = models.User_Info.objects.filter(username=username, password=password).first()
        if not user:
            ret['code'] = 404
            ret['msg'] = '用户名或密码错误'
            return JsonResponse(ret)
        token = md5(username)
        user.token = token
        user.save()
        ret['code'] = 200
        ret['token'] = token
        ret['msg'] = '登录成功'
        return JsonResponse(ret)
