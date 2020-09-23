import datetime
import json

from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
from message.models import Message
from topic.models import Topic
from user.models import UserProfile
from tools.login_decorator import login_check, get_user_by_request


@login_check("POST", "DELETE")
def topics(request, username=None):
    """
        文章模块路由
            GET:
                获取用户博客列表
                    /v1/topics/<username>
                        访问者是博主，显示所有博客列表
                            根据查询参数 ?category=xx, 做分类筛选
                        访问者是其他人 或 未登录用户 只显示 limit 值为 public 的博客列表
                获取博客内容
                    /v1/topics/<username>?t_id=00
            POST: 发表 blog
                /v1/topics/<username>
    :param username: 所访问的博客 博主 用户名
    :param request:
    :return:
    """

    if request.method == 'GET':

        # 获取博客作者
        authors = UserProfile.objects.filter(username=username)
        if not authors:
            res = {"code": 307, "error": "The current author is not existed"}
            return JsonResponse(res)
        author = authors[0]

        # 获取访问者
        visitor = get_user_by_request(request)
        visitor_name = None
        if visitor:
            visitor_name = visitor.username

        t_id = request.GET.get('t_id')

        # 获取博客列表
        if not t_id:
            category = request.GET.get('category')
            if visitor_name == username:
                # 拿所有博客
                #   分类筛选
                #   /v1/topics/username?category=tec/no-tec
                if category in ('tec', 'no-tec'):
                    view_topics = Topic.objects.filter(author_id=username, category=category)
                else:
                    view_topics = Topic.objects.filter(author_id=username)
            else:
                # 拿到 public 权限的博客
                #   分类筛选
                if category in ('tec', 'no-tec'):
                    view_topics = Topic.objects.filter(author_id=username, limit='public', category=category)
                else:
                    view_topics = Topic.objects.filter(author_id=username, limit='public')

            res = make_topics_res(author, view_topics)
            return JsonResponse(res)

        # 获取博客具体内容
        current_id = int(t_id)
        # 博主访问标记 默认 访客访问 值为 False
        is_self = False
        if visitor_name == username:
            # 博主访问
            is_self = True
            try:
                current_topic = Topic.objects.get(id=current_id)
            except Exception as e:
                result = {"code": 310, "error": "-- get blog by id - %s" % e}
                return JsonResponse(result)
        else:
            # 游客访问
            try:
                current_topic = Topic.objects.get(id=current_id, limit="public")
            except Exception as e:
                result = {"code": 310, "error": "-- get blog by id - %s" % e}
                return JsonResponse(result)

        res = make_topic_res(author, current_topic, is_self)
        return JsonResponse(res)

    elif request.method == "POST":
        user = request.user
        json_str = request.body

        if not json_str:
            # 判断字符串是否为空
            result = {"code": 302, "error": "pl transfer json.."}
            return JsonResponse(result)

        json_obj = json.loads(json_str)

        title = json_obj.get('title')

        if not title:
            # 文章标题不存在
            result = {"code": 303, "error": "pl. transfer title"}
            return JsonResponse(result)

        content = json_obj.get('content')

        # 生成文章简介
        content_text = json_obj.get('content_text')
        introduce = content_text[:30]  # 数据库存三十个中文

        limit = json_obj.get('limit')

        if limit not in ("public", "private"):
            # 权限 必须在 public private
            result = {"code": 304, "error": "limit error.."}
            return JsonResponse(result)

        category = json_obj.get('category')

        if category not in ("tec", "no-tec"):
            # 权限 必须在 public private
            result = {"code": 305, "error": "category error.."}
            return JsonResponse(result)

        now = datetime.datetime.now()

        try:
            Topic.objects.create(
                title=title,
                category=category,
                limit=limit,
                content=content,
                introduce=introduce,
                create_time=now,
                modified_time=now,
                author=user
            )
        except Exception as e:
            print('Topic create error is %s' % e)
            result = {"code": 306, "error": "The create fail!!!"}
            return JsonResponse(result)

        result = {"code": 200, 'username': user.username}
        return JsonResponse(result)

    elif request.method == "PUT":
        pass
    elif request.method == "DELETE":
        # /v1/topics/<username>?t_id=1111
        id_ = request.GET.get("t_id")
        if not id_:
            result = {"code": 308, "error": "You can't do it !!"}
            return JsonResponse(result)

        try:
            topic = Topic.objects.get(id=id_)
        except Exception as e:
            print("--delete blog -- db error...")
            result = {"code": 309, "error": "-- delete blog - topic not exist"}
            return JsonResponse(result)

        topic.delete()
        return JsonResponse({'code': 200})


def make_topics_res(author, author_topics):
    """
        获取博客列表
    :param author: 博客作者 QuerySet
    :param author_topics: 博客列表 QuerySet
    :return:
    """
    res = {"code": 200, "data": {}}
    topics_res = []

    for topic in author_topics:
        dict_topic = dict()
        dict_topic['id'] = topic.id
        dict_topic['title'] = topic.title
        dict_topic['category'] = topic.category
        dict_topic['create_time'] = topic.create_time.strftime("%Y-%m-%d %H:%M:%S")
        dict_topic['introduce'] = topic.introduce
        dict_topic['author'] = author.nickname

        topics_res.append(dict_topic)

    res['data']['topics_res'] = topics_res
    res['data']['nickname'] = author.nickname

    return res


def make_topic_res(author, author_topic, is_self):
    """
        获取博客具体内容
    :param author: 博客作者 QuerySet
    :param author_topic: 博客内容 QuerySet
    :param is_self: 博主访问标记
    :return: 
    """
    current_id = author_topic.id

    # 获取 上 / 下一个博客
    if is_self:
        # 博主自己访问
        # 取出 ID 大于当前 博客ID 的第一个数据
        # 数据库的每次查询都是新的查询，不继承任何之前的查询，每次的查询都要考虑全面
        # 确保查询到的 博客 是作者本人
        next_topic = Topic.objects.filter(id__gt=current_id, author_id=author.username).first()
        # 取出 ID 小于于当前 博客ID 的最后一个数据
        previous_topic = Topic.objects.filter(id__lt=current_id, author_id=author.username).last()
    else:
        # 访客访问
        next_topic = Topic.objects.filter(id__gt=current_id, author_id=author.username, limit="public").first()
        previous_topic = Topic.objects.filter(id__lt=current_id, author_id=author.username, limit="public").last()

    # 获取 下一个博客 id / 标题
    if next_topic:
        next_id = next_topic.id
        next_title = next_topic.title
    else:
        next_id = None
        next_title = None  # json 返回 null

    # 获取 上一个博客 id / 标题
    if previous_topic:
        previous_id = previous_topic.id
        previous_title = previous_topic.title
    else:
        previous_id = None
        previous_title = None

    result = {"code": 200, "data": {}}

    result['data']['nickname'] = author.nickname
    result['data']['title'] = author_topic.title
    result['data']['category'] = author_topic.category
    result['data']['create_time'] = author_topic.create_time.strftime('%y-%m-%d')
    result['data']['content'] = author_topic.content
    result['data']['introduce'] = author_topic.introduce
    result['data']['author'] = author.nickname
    result['data']['previous_id'] = previous_id
    result['data']['previous_title'] = previous_title
    result['data']['next_id'] = next_id
    result['data']['next_title'] = next_title

    # 获取留言数据
    msg_ = make_messages_res(author_topic)
    result['data']['message'] = msg_['msg_data']
    result['data']['message_count'] = msg_['msg_count']

    return result


def make_messages_res(author_topic):
    """
        获取 留言数据
    :param author_topic: 博客内容 QuerySet
    :return: msg_data, msg_count <type dict>
    """
    topic_id = author_topic.id
    all_messages = Message.objects.filter(topic_id=topic_id).order_by('-create_time')

    msg_list = []
    level1_msg = {}  # key: 留言ID , value： [回复对象，...]
    msg_count = all_messages.count()

    for msg in all_messages:
        if msg.parent_id:
            # 回复
            level1_msg.setdefault(msg.parent_id, [])
            level1_msg[msg.parent_id].append({
                'publisher': msg.user.nickname,
                'publisher_avatar': str(msg.user.avatar),
                'create_time': msg.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                'content': msg.content,
                'msg_id': msg.id
            })
        else:
            # 留言
            msg_ = dict()
            msg_['id'] = msg.id
            msg_['content'] = msg.content
            msg_['publisher'] = msg.user.nickname
            msg_['publisher_avatar'] = str(msg.user.avatar)
            msg_['reply'] = []
            msg_['create_time'] = msg.create_time.strftime("%Y-%m-%d %H:%M:%S")
            msg_list.append(msg_)

    # 合并 留言 回复
    for m in msg_list:
        if m['id'] in level1_msg:
            m['reply'] = level1_msg[m['id']]

    return {'msg_data': msg_list, 'msg_count': msg_count}
