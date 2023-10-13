from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework import exceptions
from server import models
from django.http import JsonResponse
import base64

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