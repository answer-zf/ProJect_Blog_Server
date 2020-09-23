"""
    检验 token
"""

import jwt
from django.http import JsonResponse

from user.models import UserProfile

KEY = "answer-zf1416"


def login_check(*methods):
    """
        使用 三层装饰器 校验 token
            目的：
                相比较两层装饰器，可以给装饰器传参
            使用：
                在需要验证的视图函数 添加 装饰器，
                将需要 token 验证的 请求 做参数传递(参数必须严格遵循书写规范)，
                该装饰器只对 所传入参数的请求做 token 验证
    :param methods: 可接受任意参数
    :return:
    """

    def _login_check(func):  # func 所装饰的 视图层函数
        def wrapper(request, *args, **kwargs):
            # token 放在 request header -> Authorization 中
            # 验证 token pyjwt 异常校验
            # 校验成功,将token中获取的username 传入 视图函数。由于安全起见，不直接使用 前端 url 传递所的 username
            # request.user = user

            token = request.META.get('HTTP_AUTHORIZATION')

            if not methods:
                # 没传递 method 参数 直接返回视图
                return func(request, *args, **kwargs)
            if request.method not in methods:
                # 校验是不是需要 token 验证的请求
                # 严格判断参数大小写 统一为大写，
                # 严格检查 methods 中的参数 是不是 "GET" "POST" "PUT" "DELETE" ... 此处略
                return func(request, *args, **kwargs)

            if not token or token == 'null':
                # 没有传递 token 返回 null
                result = {"code": 107, "error": "PL. OFFER TOKEN .."}
                return JsonResponse(result)

            # 验证 token
            try:
                payload = jwt.decode(token, KEY, algorithms='HS256')
            except Exception as e:  # 包含 exp 超时处理
                print('----token error is %s' % e)
                result = {"code": 108, "error": "PL. login .."}
                return JsonResponse(result)

            token_username = payload.get('username')
            # url_username = kwargs.get('username')
            #
            # # 前端 url 所提供的 username 校验
            # if not url_username:
            #     # 用户名不存在
            #     result = {"code": 203, "error": "pl. transfer username"}
            #     return JsonResponse(result)
            #
            # if url_username != token_username:
            #     # 用户名 与 token 不匹配
            #     result = {"code": 212, "error": "token / username mismatch..."}
            #     return JsonResponse(result)

            user = UserProfile.objects.get(username=token_username)

            if not user:
                # 用户是否存在
                result = {"code": 208, "error": "user not exist"}
                return JsonResponse(result)

            request.user = user

            return func(request, *args, **kwargs)

        return wrapper

    return _login_check


def get_user_by_request(request):
    """
        通过 request 获取用户
    :param request:
    :return: obj -> user   or   None
    """

    token = request.META.get('HTTP_AUTHORIZATION')
    if not token or token == 'null':
        return None

    try:
        res = jwt.decode(token, KEY, algorithms="HS256")
    except Exception as e:
        print("---get_user_by_request - JWT decode error is %s" % e)
        return None

    username = res['username']
    user = UserProfile.objects.get(username=username)
    return user
