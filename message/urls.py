from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^/(?P<topic_id>[0-9]+)$', views.messages, name="messages"),
    # url(r'^/(?P<username>[\w]+)/(?P<topic_id>[0-9]+)$', views.messages),
]
