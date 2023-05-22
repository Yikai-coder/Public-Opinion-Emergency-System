from django.shortcuts import render
from django.views import generic
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache  import never_cache
from django.http import HttpResponse, JsonResponse
from django.db.models import F
from .models import HotSearchItem, WeiboItem
from monitor_plan.models import MonitorPlanItem
from django.contrib.auth.models import User
from celery_tasks.tasks import traceTopic
from collections import Counter
import datetime
import operator
import copy
from django.db.models import Q
from functools import reduce
import logging

logger = logging.getLogger("hotsearch_analysis.view")
# Create your views here.
decorators = [never_cache, login_required]
sentiment_translate = {
    "happy": "高兴",
    "surprise": "惊喜",
    "neutral": "中性",
    "sad": "伤心",
    "fear": "害怕",
    "angry": "生气",
    "": "无"
}
@method_decorator(decorators, name='dispatch')
class HotSearchAnalysisView(generic.ListView):
    template_name = 'hotsearch_analysis/hotsearch_analysis.html'
    context_object_name = 'hotsearch_items'
    def get_queryset(self):
        # return MonitorPlan.objects.filter(creator_id = self.request.user.id).order_by('-created_datetime')
        days = self.kwargs['days']
        if days < 1:
            last_time = HotSearchItem.objects.order_by("-time")[:1][0].time
            return sorted(HotSearchItem.objects.filter(time=last_time), key=lambda item: item.sa_value, reverse=True)
            # return sorted(HotSearchItem.objects.order_by("-time")[:50], key=lambda item: item.sa_value, reverse=True)
        else:
            return HotSearchItem.objects.filter(time__gt=datetime.datetime.now()-datetime.timedelta(days=days)).order_by("-sa_value")[:50]
        # return HotSearchItem.objects.all()
        

def trace_hotsearch(request):
    uid = request.user.id
    hotsearch_id = request.POST['hotsearch_id']
    hotsearch = HotSearchItem.objects.get(id=hotsearch_id)
    monitor_plan = MonitorPlanItem()
    monitor_plan.name = hotsearch.title
    monitor_plan.keywords = {'keywords': ['#'+hotsearch.title+'#']}
    monitor_plan.creator = User.objects.get(id=uid)
    monitor_plan.sentiment_distribution = hotsearch.sentiment_distribution
    monitor_plan.word_cloud = hotsearch.word_cloud
    monitor_plan.save()
    # 将原来热搜爬取的微博关联到新的监控方案中
    hotsearch_weibo_items = WeiboItem.objects.filter(hotsearch_id=hotsearch)
    for item in hotsearch_weibo_items:
        item.monitor_plan_id = monitor_plan
    WeiboItem.objects.bulk_update(hotsearch_weibo_items, ['monitor_plan_id'])
    traceTopic.delay(monitor_plan_id=monitor_plan.id)
    # traceTopic(monitor_plan_id=monitor_plan.id)
    return JsonResponse(data={})

        
@method_decorator(decorators, name='dispatch')
class HotsearchDetailView(generic.DetailView):
    template_name = "hotsearch_analysis/hotsearch_detail.html"
    context_object_name = 'hotsearch_item'
    
    
    def get_object(self, queryset=HotSearchItem.objects.all()):
        obj = super().get_object(queryset)
        total_sentiment = calculate_total_sentiment(obj.sentiment_distribution)    
        obj.neutral_count = total_sentiment['neutral']
        obj.positive_count = 0
        obj.negative_count = 0
        for key in ('happy', 'surprise'):
            obj.positive_count+=total_sentiment[key]
        for key in ('sad', 'angry', 'fear'):
            obj.negative_count+=total_sentiment[key]
        obj.weibo_count = obj.positive_count+obj.negative_count+obj.neutral_count
        obj.happy_sentiment_count = total_sentiment['happy']
        obj.surprise_sentiment_count = total_sentiment['surprise']
        obj.sad_sentiment_count = total_sentiment['sad']
        obj.angry_sentiment_count = total_sentiment['angry']
        obj.fear_sentiment_count = total_sentiment['fear']
        obj.neutral_sentiment_count = total_sentiment['neutral']
        obj.wordcloud_meta = obj.word_cloud
        obj.hotweibos = WeiboItem.objects.filter(hotsearch_id=obj).exclude(type="media").annotate(total=F("reposts_count") + F("comments_count")+F("attitudes_count")).order_by("-total")[:10]        
        obj.media_weibos = WeiboItem.objects.filter(hotsearch_id=obj, type="media").annotate(total=F("reposts_count") + F("comments_count")+F("attitudes_count")).order_by("-total")[:10]

        keywords = list(obj.word_cloud.items())
        keywords.sort(key=lambda x: x[1], reverse=True)
        keywords = keywords[:10]
        keywords = [x[0] for x in keywords]
        relate_hotsearchs = []
        for keyword in keywords:
            tmp_keywords = copy.deepcopy(keywords)
            tmp_keywords.remove(keyword)
            relate_hotsearchs.append(HotSearchItem.objects.filter(title__contains=keyword).filter(reduce(operator.or_, (Q(title__contains=x) for x in tmp_keywords))).filter(time__gt=obj.time-datetime.timedelta(days=7)))
        obj.relate_hotsearchs = reduce(lambda x, y: x|y, relate_hotsearchs)
        if not obj in obj.relate_hotsearchs:
            obj.relate_hotsearchs |= HotSearchItem.objects.filter(id=obj.id)
        obj.relate_hotsearchs.order_by("time")

        for weibo in obj.hotweibos:
            weibo.sentiment = sentiment_translate[weibo.sentiment]
            weibo.created_at = weibo.created_at.strftime("%Y年%m月%d日 %H:%M")
        for weibo in obj.media_weibos:
            weibo.sentiment = sentiment_translate[weibo.sentiment]
            weibo.created_at = weibo.created_at.strftime("%Y年%m月%d日 %H:%M")
        for hotsearch in obj.relate_hotsearchs:
            hotsearch.time = hotsearch.time.strftime("%Y年%m月%d日 %H:%M")

        obj.relate_hotsearchs_start_time = obj.relate_hotsearchs[0].time
        if len(obj.sentiment_distribution.keys()) < 3:
            obj.sentiment_per_hour = {}
            weibos = obj.weiboitem_set.all()
            for weibo in weibos:
                time = weibo.created_at.strftime("%Y-%m-%d %H")
                if not time in obj.sentiment_per_hour:
                    obj.sentiment_per_hour[time] = {
                        "angry": 0,
                        "sad": 0 ,
                        "fear": 0,
                        "neutral": 0,
                        "happy": 0,
                        "surprise": 0
                    }
                obj.sentiment_per_hour[time][weibo.sentiment] += 1
            obj.sentiment_distribution = obj.sentiment_per_hour

        return obj
    
@method_decorator(decorators, name='dispatch')
class HotsearchTrendView(generic.TemplateView):
    template_name = "hotsearch_analysis/hotsearch_trend.html"
    # context_object_name = "trend_dict"
    
    def get_context_data(self, queryset=HotSearchItem.objects.filter(time__gt=datetime.datetime.now()-datetime.timedelta(days=7)).all()):
        
        trend_dict = super().get_context_data(queryset = queryset)
        hotsearch_items = queryset
        trend_dict["hotsearch_count"] = len(hotsearch_items)
        trend_dict["positive_count"] = len(hotsearch_items.filter(dominant_sentiment__in = ("happy", "surprise")))
        trend_dict["neutral_count"] = len(hotsearch_items.filter(dominant_sentiment="neutral"))
        trend_dict['negative_count'] = len(hotsearch_items.filter(dominant_sentiment__in = ("sad", "fear", "angry")))

        trend_dict["total_sentiment_distribution"] = {
            "angry": 0,
            "sad": 0 ,
            "fear": 0,
            "neutral": 0,
            "happy": 0,
            "surprise": 0
        }
        trend_dict["word_cloud_meta"] = {}
        trend_dict["sentiment_each_date"] = {}
        for hotsearch_item in hotsearch_items:
            if hotsearch_item.dominant_sentiment in ("happy", "surprise", "neutral", "sad", "angry", "fear"):
                trend_dict["total_sentiment_distribution"][hotsearch_item.dominant_sentiment] += 1
                if not str(hotsearch_item.time.date()) in trend_dict['sentiment_each_date']:
                    trend_dict['sentiment_each_date'][str(hotsearch_item.time.date())] = {
                        "angry": 0,
                        "sad": 0 ,
                        "fear": 0,
                        "neutral": 0,
                        "happy": 0,
                        "surprise": 0
                    }
                trend_dict['sentiment_each_date'][str(hotsearch_item.time.date())][hotsearch_item.dominant_sentiment] += 1
            trend_dict["word_cloud_meta"] = dict(Counter(trend_dict["word_cloud_meta"]) + Counter(hotsearch_item.word_cloud))
        return trend_dict
        
def calculate_total_sentiment(sentiment_distribution):
    total_sentiment = {
            "angry": 0,
            "sad": 0 ,
            "fear": 0,
            "neutral": 0,
            "happy": 0,
            "surprise": 0
        }
    if sentiment_distribution is None:
        return total_sentiment
    for date in sentiment_distribution.keys():
        for sentiment in sentiment_distribution[date].keys():
            if sentiment in total_sentiment:
                total_sentiment[sentiment] += sentiment_distribution[date][sentiment]
            else:
                total_sentiment[sentiment] = sentiment_distribution[date][sentiment]
    return total_sentiment