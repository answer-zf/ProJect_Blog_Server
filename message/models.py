from django.db import models

# Create your models here.
from topic.models import Topic
from user.models import UserProfile


class Message(models.Model):
    topic = models.ForeignKey(Topic)
    content = models.CharField(verbose_name="留言内容", max_length=100)
    user = models.ForeignKey(UserProfile)
    parent_id = models.IntegerField(verbose_name="父留言")
    create_time = models.DateTimeField()

    class Meta:
        db_table = "message"
