from django.conf.urls import url

from . import views

# 主模块路由：/v1/users

urlpatterns = [
    url(r'^$', views.users, name='users'),
    # /v1/users/username
    url(r'^/(?P<username>[\w]{6,11})$', views.users, name='user'),
    # /v1/users/username/avatar
    url(r'^/(?P<username>[\w]{6,11})/avatar$', views.user_avatar, name='user_avatar'),
]
