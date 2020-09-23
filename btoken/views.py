import jwt
import time
import json
import hashlib
from django.http import JsonResponse

from user.models import UserProfile


def btoken(request):
    """
        创建 token （用户登录）
    :param request:
    :return: json
    """
    if request.method != "POST":
        # 当前视图只接受 POST 请求
        result = {"code": 101, "error": "pl. use POST"}
        return JsonResponse(result)

    json_str = request.body

    if not json_str:
        # 前端异常，提交空数据
        result = {"code": 102, "error": "pl. transfer data"}
        return JsonResponse(result)

    json_obj = json.loads(json_str)
    username = json_obj.get('username')
    password = json_obj.get('password')

    # 前端数据 验证
    if not username:
        # 用户名不存在
        result = {"code": 103, "error": "pl. transfer username"}
        return JsonResponse(result)

    if not password:
        # 密码不存在
        result = {"code": 104, "error": "pl. transfer password"}
        return JsonResponse(result)

    userinfo = UserProfile.objects.filter(username=username)

    if not userinfo:
        # 当前用户不存在
        result = {"code": 105, "error": "user not exist!!"}
        return JsonResponse(result)

    # 密码验证
    pw_sha = hashlib.sha1()
    pw_sha.update(password.encode())

    if pw_sha.hexdigest() != userinfo[0].password:
        # 用户名、密码 不匹配
        result = {"code": 106, "error": "The username or the password is wrong!!!"}
        return JsonResponse(result)

    # 生成 token
    token = make_token(username)
    result = {
        "code": 200,
        "username": username,
        "data": {
            "token": token.decode()
        }
    }
    return JsonResponse(result)


def make_token(username, expire=3600 * 24):
    """
        生成 token
    :param username: 用户名 str
    :param expire: 过期时间 int ，默认 1 天
    :return: token bytes
    """
    key = "answer-zf1416"
    exp = int(time.time() + expire)
    payload = {
        "username": username,
        "exp": exp
    }

    return jwt.encode(payload, key, algorithm="HS256")
