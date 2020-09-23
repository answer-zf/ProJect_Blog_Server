import hashlib
import json

from django.http import JsonResponse

from btoken.views import make_token
from tools.login_decorator import login_check
from user.models import UserProfile


@login_check('PUT', 'DELETE')
def users(request, username=None):
    """
        用户模块 路由
            GET ： 获取用户信息
            POST:  注册（创建用户信息）
            PUT :  修改用户信息
    :param username: 通过 url 传递的用户名
    :param request: 请求
    :return: json
    """
    if request.method == 'GET':
        print(username)
        # 取数据
        if username:
            # 具体用户数据

            # 利用 视图传参 和 查询字符串相结合 的方式，获取 某一用户信息内的 某一个字段内容
            # /v1/users/username?info=1 返回 {info:xxx}

            try:
                user = UserProfile.objects.get(username=username)
            except UserProfile.DoesNotExist:
                user = None

            if not user:
                # 用户不存在
                result = {"code": 208, "error": "user not exist"}
                return JsonResponse(result)

            # 判断查询字符串
            if request.GET.keys():
                data = {}
                for key in request.GET.keys():
                    if hasattr(user, key):
                        data[key] = getattr(user, key)
                result = {
                    "code": 200,
                    "username": username,
                    "data": data
                }
                return JsonResponse(result)
            else:
                # 指定查询用户全量数据
                result = {
                    "code": 200,
                    "username": username,
                    "data": {
                        "nickname": user.nickname,
                        "info": user.info,
                        "sign": user.sign,
                        "avatar": str(user.avatar)
                    }
                }
                return JsonResponse(result)
        else:
            # 全部用户数据

            all_users = UserProfile.objects.all()
            dict_res = []

            for item in all_users:
                item_d = dict()
                item_d['username'] = item.username
                item_d['email'] = item.email
                item_d['sign'] = item.sign
                item_d['info'] = item.info
                dict_res.append(item_d)

            result = {
                "code": 200,
                "data": dict_res
            }
            return JsonResponse(result)

    elif request.method == 'POST':
        # 注册
        # 密码 SHA-1

        # 获取json 数据
        json_str = request.body
        if not json_str:
            # 前端异常，提交空数据
            result = {"code": 202, "error": "pl. transfer data"}
            return JsonResponse(result)

        # 反序列化 json_str
        json_obj = json.loads(json_str)
        username = json_obj.get('username')
        email = json_obj.get('email')
        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')

        # 前端数据 验证
        if not username:
            # 用户名不存在
            result = {"code": 203, "error": "pl. transfer username"}
            return JsonResponse(result)

        if not email:
            # 邮箱不存在
            result = {"code": 204, "error": "pl. transfer email"}
            return JsonResponse(result)

        if not password_1 or not password_2:
            # 密码不存在
            result = {"code": 205, "error": "pl. transfer password"}
            return JsonResponse(result)

        if password_1 != password_2:
            # 两次输入的密码，不一致
            result = {"code": 206, "error": "The two passwords do not agree"}
            return JsonResponse(result)

        # 验证用户 是否已存在
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {"code": 207, "error": "The username is existed!!!"}
            return JsonResponse(result)

        # SHA-1 散列加密
        pw_sha = hashlib.sha1()
        pw_sha.update(password_1.encode())

        # 存入数据
        try:
            UserProfile.objects.create(
                username=username,
                nickname=username,
                email=email,
                password=pw_sha.hexdigest()
            )
        except Exception as e:
            print('UserProfile create error is %s' % e)
            result = {"code": 207, "error": "The username is existed!!!"}
            return JsonResponse(result)

        # 根据用户名，生成 token
        token = make_token(username)
        result = {
            "code": 200,
            "username": username,
            "data": {
                "token": token.decode()
            }
        }
        return JsonResponse(result)

    elif request.method == 'PUT':

        # 更新数据
        user = request.user
        json_str = request.body

        if not json_str:
            # 前端是否传递数据
            result = {"code": 202, "error": "pl. transfer data"}
            return JsonResponse(result)

        json_obj = json.loads(json_str)

        nickname = json_obj.get('nickname')
        if not nickname:
            # 昵称不能为空
            result = {"code": 209, "error": "pl. transfer nickname"}
            return JsonResponse(result)

        sign = json_obj.get('sign', '')
        info = json_obj.get('info', '')

        user.nickname = nickname
        user.sign = sign
        user.info = info
        user.save()

        result = {"code": 200, "username": username}
        return JsonResponse(result)

    elif request.method == 'DELETE':

        user = request.user
        user.delete()

        result = {
            "code": 200,
            "data": "User Deleted..."
        }

        return JsonResponse(result)


@login_check("POST")
def user_avatar(request, username):
    """
        处理上传文件 form 提交
            只需 拿到 post 提交 request.FILES['avatar']
            由于 django 获取 PUT 请求的 multipart数据 较为复杂，故采用 POST 请求处理 multipart数据
    :param username: 通过 url 传递的用户名
    :param request:
    :return:
    """
    if request.method != "POST":
        # 昵称不能为空
        result = {"code": 210, "error": "PL. USE POST"}
        return JsonResponse(result)

    avatar = request.FILES.get('avatar')

    if not avatar:
        # 没用提交图片信息
        result = {"code": 211, "error": "pl. upload avatar"}
        return JsonResponse(result)

    user = request.user

    try:
        user.avatar = avatar
        user.save()
    except Exception as e:
        # 修改数据库内容失败
        print('UserProfile create error is %s' % e)
        result = {"code": 211, "error": "pl. upload avatar......"}
        return JsonResponse(result)

    result = {"code": 200, "username": username}
    return JsonResponse(result)
