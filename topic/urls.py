from django.conf.urls import url

from . import views

# /v1/topic/author_id

urlpatterns = [
    url(r'^/(?P<username>[\w]+)$', views.topics, name='topics')
]
