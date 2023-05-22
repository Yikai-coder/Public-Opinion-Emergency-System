from django.shortcuts import render
from django.views import generic
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache  import never_cache
from monitor_plan.models import MonitorPlanItem
import datetime
# Create your views here.
decorators = [never_cache, login_required]

@method_decorator(decorators, name='dispatch')
class HomeView(generic.ListView):
    template_name = 'home/home.html'
    context_object_name = 'latest_monitor_plans'

    def get_queryset(self):
        items = MonitorPlanItem.objects.filter(creator_id = self.request.user.id).order_by('-created_datetime')
        for item in items:
            item.created_datetime = item.created_datetime.strftime("%Y年%m月%d日 %H:%M")
        return items