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
        if request.method == "GET":
            token = request.GET.get('token')
        else:
            token = request.data.get('token')
        token_obj = models.User_Info.objects.filter(token=token).first()
        if not token_obj:
            raise exceptions.AuthenticationFailed('token失效或错误')
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
        user = request.user
        try:
            pos = room.member.split(',').index(user.username)
        except ValueError:
            ret['status_code'] = 403
            ret['msg'] = '玩家不在此房间中'
            return JsonResponse(ret)
        if(room.ready.split(',')[pos] == '1'):
            ret['self_ready'] = True
        else:
            ret['self_ready'] = False
        ret['status_code'] = 200
        ret['msg'] = '获取成功'
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
        lexicon_id = request.POST.get('lexicon_id')
        if not lexicon_id:
            ret['status_code'] = 404
            ret['msg'] = '请求参数错误'
            return JsonResponse(ret)
        for _ in range(8):
            room_id += chr(random.randint(97, 122)) # TODO 此处存在问题，可能产生同样的roomid
        models.Room_Info.objects.create(room_id=room_id, owner=owner.username, member=owner.username, lexicon_id=lexicon_id, ready='1') #TODO 待修复 Room id 应当为unique的
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
        if not room_id:
            ret['status_code'] = 404
            ret['msg'] = '请求参数错误'
            return JsonResponse(ret)
        room = models.Room_Info.objects.filter(room_id=room_id).first()
        if not room:
            ret['status_code'] = 403
            ret['msg'] = '房间不存在'
            return JsonResponse(ret)
        if room.state:
            ret['status_code'] = 403
            ret['msg'] = '房间已开始'
            return JsonResponse(ret)
        member = room.member.split(',')
        if user.username in member:
            ret['status_code'] = 403
            ret['msg'] = '已在房间内'
            return JsonResponse(ret)
        room.member = room.member + ',' + user.username # TODO 这样如果用户名存在,会有问题，可以改为jsonField存储列表
        room.ready = room.ready + ',' + '0'
        room.save()
        ret['status_code'] = 200
        ret['msg'] = '加入成功'
        return JsonResponse(ret) # TODO 如果房间满人应该做出处理


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
                ret['status_code'] = 201
                ret['msg'] = '有人未准备'
            else:
                room.state = 1
                with open('server/lexicon.json', encoding='utf-8') as f:
                    lexicon_data = json.load(f)
                sort = ["动物类", "植物类", "食品类", "交通工具", "日常用品", "地点和建筑", "职业", "活动和娱乐"]
                lexicon = lexicon_data[sort[room.lexicon_id]]
                res = sample(lexicon, len(member))
                for i in range(len(res)):
                    models.Work_info.objects.create(username=member[i], room_id=room_id, round=1, category=1,
                                                    word=res[i])
                for i in range(len(res)):
                    if i == 0:
                        models.Round_info.objects.create(room_id = room_id, round = i+1, round_state = 0)
                    else:
                        models.Round_info.objects.create(room_id = room_id, round = i+1, round_state = -1)
                room.round = 1
                room.save()
                ret['status_code'] = 200
                ret['msg'] = '开始游戏成功'
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
                ready_text = ready_text + ',' + ready[i] # TODO 字符串拼接待优化
            room.ready = ready_text
            room.save()
        return JsonResponse(ret)


class Lexicon(APIView):
    authentication_classes = [Authtication, ]

    def post(self, request):
        ret = {}
        room_id = request.POST.get('room_id')
        lexicon_id = request.POST.get('lexicon_id')
        if not room_id or not lexicon_id:
            ret['status_code'] = 404
            ret['msg'] = '请求参数错误'
            return JsonResponse(ret) 
        if int(lexicon_id) < 0 or int(lexicon_id) > 7:
            ret['status_code'] = 404
            ret['msg'] = '词库号错误'
            return JsonResponse(ret)
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
        username = request.user.username
        if not room_id or not round or not username:
            ret['status_code'] = 404
            ret['msg'] = '请求参数错误'
            return JsonResponse(ret) 
        work = models.Work_info.objects.filter(room_id=room_id, round=round, username=username).first()
        if not work:
            ret['status_code'] = 404
            ret['msg'] = '参数错误'
            return JsonResponse(ret)
        if work.category == 1:
            ret['status_code'] = 200
            ret['word'] = work.word
            ret['img'] = ''
            ret['type'] = 1
            ret['msg'] = '获取成功'
        else:
            ret['status_code'] = 200
            ret['word'] = ''
            ret['img'] = work.img
            ret['type'] = 0
            ret['msg'] = '获取成功'
        return JsonResponse(ret)


class Submit(APIView):
    authentication_classes = [Authtication, ]

    def post(self, request):
        ret = {}
        user = request.user
        room_id = request.POST.get('room_id')
        is_word = request.POST.get('is_word')
        round = request.POST.get('round')
        if not room_id or not is_word or not round:
            ret['status_code'] = 404
            ret['msg'] = '请求参数错误'
            return JsonResponse(ret) 
        room = models.Room_Info.objects.filter(room_id=room_id).first()
        if not room:
            ret['status_code'] = 403
            ret['msg'] = '房间不存在'
            return JsonResponse(ret)
        round_info = models.Round_info.objects.filter(room_id=room_id, round = round)
        if round_info.round_state == -1:
            ret['status_code'] = 402
            ret['msg'] = '未进入该回合'
            return JsonResponse(ret)
        elif round_info.round_state == 0:
            ret['status_code'] = 401
            ret['msg'] = '玩家未全部准备好'
            return JsonResponse(ret)
        elif round_info.round_state == 3:
            ret['status_code'] = 400
            ret['msg'] = '回合已结束不允许提交'
            return JsonResponse(ret)
        submit_member = round_info.submit_member.split(',')
        if user.username in submit_member:
            ret['status_code'] = 200
            ret['msg'] = '玩家本轮已提交答案'
            return JsonResponse(ret) 
        if is_word == '1': # 提交的是词语
            word = request.POST.get('word')
            work_info = models.Work_info.objects.filter(room_id=room_id, round=round, username=user.username, category = 0).first()
            work_info.word = word
            work_info.save()
        else:
            img = request.POST.get('img')
            work_info = models.Work_info.objects.filter(room_id=room_id, round=round, username=user.username, category = 1).first()
            work_info.img = img
            work_info.save()

        round_info.submit_num += 1
        submit_member.append(user.username)
        round_info.submit_member = ','.join(submit_member)
        round_finish_flag = False
        if round_info.submit_num == len(room.member.split(',')):
            round_info.round_state = 3
            round_finish_flag = True
        round_info.save()

        if round_finish_flag:
            room.round = room.round + 1
            room.save()
            nxt_round_info = models.Round_info.objects.filter(room_id=room_id, round = room.round).first()
            if nxt_round_info: # 全部结束时没有下一轮
                nxt_round_info.round_state = 0
                member = room.member.split(',')
                if is_word == "1": # 上一轮提交词语，本轮问题应该是词语，本轮cate为1，上轮cate为0
                    for i, user in enumerate(member):
                        prework = models.Work_info.objects.filter(room_id=room_id, round = room.round-1, username=member[i-1], category = 0).first()
                        models.Work_info.objects.create(username = member[i], room_id=room_id, round = room.round, category = 1, word=prework.word)
                else: # 上一轮提交图片，本轮问题应该是图片，本轮cate为0，上轮cate为1
                    for i, user in enumerate(member):
                        prework = models.Work_info.objects.filter(room_id=room_id, round = room.round-1, username=member[i-1], category = 1).first()
                        models.Work_info.objects.create(username = member[i], room_id=room_id, round = room.round, category = 0, img=prework.img)
            else:
                member = room.member.split(',')
                for i, user in enumerate(member):
                    models.Question_Vote.objects.create(
                        room_id = room_id,
                        answer_seq = ','.join(member[i:]+member[:i])
                    )
        ret['status_code'] = 200
        ret['msg'] = '提交成功'
        return JsonResponse(ret)

class Ready(APIView):
    authentication_classes = [Authtication, ]

    def get(self, request):
        ret = {}
        user = request.user
        room_id = request.GET.get('room_id')
        room = models.Room_Info.objects.filter(room_id = room_id).first()
        if not room:
            ret['status_code'] = 404
            ret['msg'] = '房间号错误'
            return JsonResponse(ret)
        round = request.GET('round')
        round_info = models.Round_info.objects.filter(room_id = room_id, round = round)
        if not round_info:
            ret['status_code'] = 404
            ret['msg'] = '轮次错误'
            return JsonResponse(ret)
        if round_info.round_state == -1:
            ret['status_code'] = 403
            ret['msg'] = '未进入该回合'
            return JsonResponse(ret)
        elif round_info.round_state == 0:
            member = round_info.ready_member.split(',')
            if user.username in member:
                ret['status_code'] = 200
                ret['msg'] = '玩家本轮已准备'
                return JsonResponse(ret)
            member.append(user.username)
            round_info.ready_num += 1
            round_info.ready_member = ','.join(member)
            tot_num = len(room.member.split(','))
            if round_info.ready_num == tot_num:
                import time
                round_info.round_state = 1
                round_info.start_time = int(time.time())
            round_info.save()
            ret['status_code'] = 200
            ret['msg'] = '本轮准备成功'
        else:
            ret['status_code'] = 402
            ret['msg'] = '回合正在进行或已结束'
            return JsonResponse(ret)

# TODO 处理游戏过程的断线
class Round(APIView):
    authentication_classes = [Authtication, ]

    def get(self, request):
        import time
        STATE2_TIMEOUT = 60000 # 60s
        ret = {}
        user = request.user
        room_id = request.GET.get('room_id')
        room = models.Room_Info.objects.filter(room_id=room_id).first()
        if not room:
            ret['status_code'] = 404
            ret['msg'] = '房间号错误'
            return JsonResponse(ret)
        if room.round == len(room.member.split(','))+1:
            ret['status_code'] = 200
            ret['msg']='获取成功'
            ret['round_state'] = 3
            ret['is_finished'] = True
            return JsonResponse(ret)
        round_info = models.Round_info.objects.filter(room_id=room_id, round = room.round)
        if not round_info:
            ret['status_code'] = 404
            ret['msg'] = '轮数错误'
            return JsonResponse(ret)
        ret['round_state'] = round_info.round_state
        ret['submit_num'] = round_info.submit_num
        ret['start_time'] = round_info.start_time
        ret['ready_num'] = round_info.ready_num
        ret['is_ready'] = user.username in round_info.ready_member.split(',')
        ret['is_submit'] = user.username in round_info.submit_member.split(',')
        ret['status_code'] = 200
        ret['round'] = room.round
        ret['is_finished'] = False
        ret['msg']='获取成功'
        if round_info.round_state == 1 and (time.time() - round_info.start_time > STATE2_TIMEOUT): # 状态1超时
            round_info.round_state = 2
            round_info.save()
        return JsonResponse(ret)


class Vote(APIView): # TODO 需要重置以适应多轮展示
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


class Exit(APIView):
    authentication_classes = [Authtication, ]

    def post(self, request):
        ret = {}
        room_id = request.POST.get('room_id')
        user = request.user
        room = models.Room_Info.objects.filter(room_id=room_id).first()
        print(not room)
        if not room:
            ret['status_code'] = 404
            ret['msg'] = '房间未找到'
            return JsonResponse(ret)
        if user.username == room.owner:
            room.delete()
            ret['status_code'] = 200
            ret['msg'] = '房间已解散'
            return JsonResponse(ret)
        member = room.member.split(',')
        ready = room.ready.split(',')
        if user.username not in member:
            ret['status_code'] = 403
            ret['msg'] = '不在房间内'
            return JsonResponse(ret)
        new_member_list = member[0]
        new_ready_list = ready[0]
        for i in range(1, len(member)):
            if user.username != member[i]:
                new_member_list = new_member_list + ',' + member[i]
                new_ready_list = new_ready_list + ',' + ready[i]
        room.member = new_member_list
        room.ready = new_ready_list
        room.save()
        ret['status_code'] = 200
        ret['msg'] = '房间已退出'
        return JsonResponse(ret)
