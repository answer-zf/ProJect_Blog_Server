from django.conf.urls import url

from . import views

# 主模块路由：http://..../v1/tokens

urlpatterns = {
    url(r'^$', views.btoken, name='btoken'),
}
