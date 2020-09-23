from django.db import models

# Create your models here.
from user.models import UserProfile


class Topic(models.Model):
    title = models.CharField(max_length=50, verbose_name="文章标题")
    # tec 技术类 & no-tec 非技术类
    category = models.CharField(verbose_name="文章分类", max_length=20)
    # public 公开的 【所有人都能看】
    # private 私有的 【只有文章作者本人能看】
    limit = models.CharField(verbose_name="文章权限", max_length=10)
    introduce = models.CharField(verbose_name="文章简介", max_length=90)
    content = models.TextField(verbose_name="文章内容")
    create_time = models.DateTimeField()
    modified_time = models.DateTimeField()
    author = models.ForeignKey(UserProfile)

    class Meta:
        db_table = 'topic'
