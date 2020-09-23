"""blog_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'^text_api$', views.text_api),
    # 添加 user 模块 url 映射
    url(r'^v1/users', include('user.urls')),
    # 添加 btoken 模块 url 映射(用于登录操作)
    url(r'^v1/tokens', include('btoken.urls')),
    # 添加 topic 模块 url 映射
    url(r'^v1/topics', include('topic.urls')),
    # 添加 message 模块 url 映射
    url(r'^v1/messages', include('message.urls')),
]
# 添加图片的 路由映射  http://127.0.0.0:8000/media/xxx.jpg
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
