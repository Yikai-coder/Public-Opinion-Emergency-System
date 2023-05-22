import django
from django.db import models
from django.contrib.auth.models import User
import datetime
# Create your models here.
class MonitorPlanItem(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(null=True)
    keywords = models.JSONField()
    exclude_words = models.JSONField(null=True)
    creator = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created_datetime = models.DateTimeField(default=django.utils.timezone.now)
    last_update = models.DateTimeField(auto_created=True, default=django.utils.timezone.now)
    sentiment_distribution = models.JSONField(null=True)
    word_cloud = models.JSONField(null=True)