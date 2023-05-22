from django.db import models
from monitor_plan.models import MonitorPlanItem

# Create your models here.
class HotSearchItem(models.Model):
    rank = models.FloatField()
    title = models.CharField(max_length=30, verbose_name="热搜话题")
    degree = models.IntegerField()
    time = models.DateTimeField()
    url = models.URLField(max_length=500)
    sentiment_distribution = models.JSONField(null=True)
    word_cloud = models.JSONField(null=True)
    negative_sentiment_portion = models.FloatField(default=0)
    read_count = models.IntegerField(default=0)
    discussion_count = models.IntegerField(default=0)
    sa_value = models.FloatField(default=0)
    dominant_sentiment = models.CharField(max_length=10, blank=True)
    class Meta:
        verbose_name_plural = '热搜爬虫item'
    def __str__(self):
        return self.title
    
class WeiboItem(models.Model):
    mid = models.CharField(max_length=18)
    bid = models.CharField(max_length=10)
    user_id = models.CharField(max_length=10)
    nick_name = models.CharField(max_length=30)
    text = models.TextField()
    article_url = models.URLField(max_length=500)
    location =  models.CharField(max_length=30)
    # at_users = models.TextField()
    at_users = models.JSONField(null=True)
    # topics = models.CharField(max_length=60)
    topics = models.JSONField(null=True)
    reposts_count = models.IntegerField()
    comments_count = models.IntegerField()
    attitudes_count = models.IntegerField()
    created_at = models.DateTimeField()
    source = models.CharField(max_length=15)
    # pics = models.CharField(max_length=200)
    # pics = models.URLField()
    pics = models.JSONField(null=True)
    video_url = models.URLField(max_length=500)
    retweet_id = models.CharField(max_length=30)
    hotsearch_id = models.ForeignKey(to=HotSearchItem, on_delete=models.CASCADE, null=True)
    monitor_plan_id = models.ForeignKey(to=MonitorPlanItem, on_delete=models.CASCADE, null=True)
    sentiment = models.CharField(max_length=10, blank=True)
    type = models.CharField(max_length=10, blank=True)
    class Meta:
        verbose_name_plural = '微博博文item'
    def __str__(self):
        return self.text if len(self.text) < 15 else self.text[:15]+"..."