import json
from datetime import datetime

from django.shortcuts import render

from django.http import JsonResponse

# Create your views here.
from message.models import Message
from tools.login_decorator import login_check
from topic.models import Topic


@login_check("POST")
def messages(request, topic_id):
    """
        创建留言信息
    :param request:
    :param topic_id: 所留言的文章id
    :return:
    """
    if request.method == "POST":
        user_ = request.user

        if not topic_id:
            result = {"code": 601, "error": "pl. transfer topic_id"}
            return JsonResponse(result)

        try:
            topic_ = Topic.objects.get(id=topic_id)
        except Exception as e:
            result = {"code": 602, "error": "-- post message - select topic for id error is %s" % e}
            return JsonResponse(result)

        # 文章权限校验
        #    非法访问 防护  网络安全。。
        if topic_.limit == "private":
            if user_.username != topic_.author.username:
                result = {"code": 606, "error": "-- post message - forbidden for limit .."}
                return JsonResponse(result)

        str_msg = request.body
        if not str_msg:
            result = {"code": 603, "error": "-- post message - not transfer JSON"}
            return JsonResponse(result)
        obj_msg = json.loads(str_msg)

        content = obj_msg.get('content')
        parent_id = obj_msg.get('parent_id', 0)

        if not content:
            result = {"code": 605, "error": "-- post message - content not exist.."}
            return JsonResponse(result)

        try:
            Message.objects.create(
                content=content,
                create_time=datetime.now(),
                user=user_,
                topic=topic_,
                parent_id=parent_id
            )
        except Exception as e:
            result = {"code": 604, "error": "-- post message - create message for id error is %s" % e}
            return JsonResponse(result)

        result = {"code": 200, "data": {}}
        result["data"]['content'] = content
        return JsonResponse(result)
