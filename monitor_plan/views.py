from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from monitor_plan.models import MonitorPlanItem
from hotsearch_analysis.models import WeiboItem
from django.views import generic
from django.utils import timezone
from django.db.models import F

from celery_tasks.tasks import traceTopic 

sentiment_translate = {
    "happy": "高兴",
    "surprise": "惊喜",
    "neutral": "中性",
    "sad": "伤心",
    "fear": "害怕",
    "angry": "生气",
    "": "无"
}
# Create your views here.
def plan_delete(request):
    plan_id = request.GET['plan_id']
    MonitorPlanItem.objects.filter(id=plan_id).delete()
    return JsonResponse(data={})

class PlanView(generic.DetailView):
    template_name = "monitor_plan/detail.html"
    context_object_name = 'item'
    
    def get_object(self, queryset=MonitorPlanItem.objects.all()):
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
        obj.hotweibos = []
        obj.hotweibos = WeiboItem.objects.filter(monitor_plan_id=obj).annotate(total=F("reposts_count") + F("comments_count")+F("attitudes_count")).order_by("-total")[:10]        
        obj.media_weibos = WeiboItem.objects.filter(monitor_plan_id=obj, type="media").annotate(total=F("reposts_count") + F("comments_count")+F("attitudes_count")).order_by("-total")[:10]


        for weibo in obj.hotweibos:
            weibo.sentiment = sentiment_translate[weibo.sentiment]
            weibo.created_at = weibo.created_at.strftime("%Y年%m月%d日 %H:%M")
        for weibo in obj.media_weibos:
            weibo.sentiment = sentiment_translate[weibo.sentiment]
            weibo.created_at = weibo.created_at.strftime("%Y年%m月%d日 %H:%M")

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

class ModifyView(generic.DetailView):
    template_name = "monitor_plan/modify.html"
    model = MonitorPlanItem
    context_object_name = "monitor_plan"

    def post(self, request, pk):
        uid = None
        if not request.user.is_authenticated:
            return JsonResponse(data={'code':-1, 'msg': "User hasn't log in"})            
        uid = request.user.id
        plan_id = request.POST["plan_id"]
        plan_name = request.POST["plan_name"]
        plan_description = request.POST["plan_description"]
        plan_keywords = request.POST.getlist("plan_keywords[]")
        plan_excludewords = request.POST.getlist("plan_excludewords[]")
        self.model.objects.filter(id=plan_id).delete()
        monitor_plan = self.model.objects.create(
            name = plan_name,
            description = plan_description,
            keywords = {'keywords': plan_keywords},
            exclude_words = {'exlude_words': plan_excludewords},
            created_datetime = timezone.now(),
            creator_id = uid
        )
        monitor_plan.save()
        traceTopic.delay(monitor_plan.id)
        return JsonResponse(data={'code': 1})

class AddView(generic.TemplateView):
    template_name = "monitor_plan/add.html"
    model = MonitorPlanItem

    def post(self, request):
        uid = None
        if not request.user.is_authenticated:
            return JsonResponse(data={'code':-1, 'msg': "User hasn't log in"})   
        self.add_monitor_plan(uid=request.user.id, plan_name=request.POST["plan_name"], plan_description=request.POST["plan_description"],
                         plan_keywords=request.POST.getlist("plan_keywords[]"), plan_excludewords=request.POST.getlist("plan_excludewords[]"))         
        return JsonResponse(data={'code': 1})

    def add_monitor_plan(self, uid, plan_name, plan_description, plan_keywords, plan_excludewords):
        monitor_plan = self.model.objects.create(
            name = plan_name,
            description = plan_description,
            keywords = {'keywords': plan_keywords},
            exclude_words = {'exlude_words': plan_excludewords},
            created_datetime = timezone.now(),
            creator_id = uid
        )
        monitor_plan.save()
        traceTopic.delay(monitor_plan.id)

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