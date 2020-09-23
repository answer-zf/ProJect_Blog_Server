from django.http import JsonResponse


def text_api(request):
    return JsonResponse({'code': 200})
    # 1. 将返回内容序列化为 json
    # 2. response中添加响应头 content-type: application/json
