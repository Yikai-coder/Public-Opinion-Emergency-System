import os, sys
from celery import platforms
from scrapy.crawler import CrawlerProcess
from billiard import Process
from scrapy.utils.project import get_project_settings
import datetime
from scrapy.crawler import CrawlerProcess
import psutil

from peos import celery_app 
from celery_tasks.spider.weibo.spiders.keyword_search import KeyWordSearchSpider
# from crontab_app.spider.weibo.spiders.keyword_search import KeyWordSearchSpider
from monitor_plan.models import MonitorPlanItem
from crontab_app.sentiment.bert.test import test
from crontab_app.word_cloud.wordcloud import generate_wordcloud_meta
from crontab_app.cron import sentimentAnalysis, generateWordCloud, updateSettingsCookies
from public.utils import check_connection

class CrawlerScript(Process):
    def __init__(self, spider, settings):
        Process.__init__(self)
        self.crawler = CrawlerProcess(settings)
        self.spider = spider

    def run(self):
        self.crawler.crawl(self.spider)
        self.crawler.start()

def runSearchSpider(keyword_list:list=None, start_date:str=None, end_date:str=None, region:list=None, weibo_type:int=None, further_threshold:int=None, monitor_plan:object=None, type:int=0):
    """启动搜索爬虫，对新生成的monitor_plan中的关键词进行搜索并爬取微博

    Args:
        keyword_list (list, optional): 关键词列表. Defaults to None.
        start_date (str, optional): 开始日期. Defaults to None.
        end_date (str, optional): 截止日期. Defaults to None.
        region (list, optional): 地区. Defaults to None.
        weibo_type (int, optional): 微博类型. Defaults to None.
        further_threshold (int, optional): 细分搜索页数门槛，当搜索结果页数多于它时，会根据时间和地区进一步进行划分，再进行爬取，避免对一个搜索结果长时间爬取. Defaults to None.
        monitor_plan (object, optional): 对应的监控方案. Defaults to None.
    """
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', "celery_tasks.spider.weibo.settings")  # 需要设置环境变量让get_project_settings能够找到settings.py
    settings = get_project_settings()
    if not keyword_list is None:
        settings.set('KEYWORD_LIST', keyword_list)
    if not start_date is None:
        settings.set("START_DATE", start_date)
    if not end_date is None:
        settings.set("END_DATE", end_date)
    if not region is None:
        settings.set("REGION", region)
    if not weibo_type is None:
        settings.set("WEIBO_TYPE", weibo_type)
    if not further_threshold is None:
        settings.set("FURTHER_THRESHOLD", further_threshold)
    settings.set("MONITOR_PLAN", monitor_plan)
    settings.set("WEIBO_TYPE", type)
    spider = KeyWordSearchSpider
    crawler = CrawlerScript(spider, settings)
    crawler.start()
    crawler.join()


platforms.C_FORCE_ROOT = True
    
@celery_app.task
def traceTopic(monitor_plan_id):
    """启动对某个monitor_plan的追踪
    1.启动搜索爬虫爬取该事件n天前到现在为止的所有微博
    2.对关联的所有微博进行情感分析
    3.对关联的所有微博生成词云

    Args:
        monitor_plan_id (int): 

    """
    # check_connection()
    monitor_plan = MonitorPlanItem.objects.get(id=monitor_plan_id)
    updateSettingsCookies()
    for type in (5, 2, 1):
        runSearchSpider(keyword_list=monitor_plan.keywords['keywords'], 
                        start_date=(datetime.datetime.now()-datetime.timedelta(days=3)).strftime('%Y-%m-%d'),
                        end_date=datetime.datetime.now().strftime('%Y-%m-%d'),
                        monitor_plan = monitor_plan,
                        type=type
        )
    # 每次跟踪只针对一个monitor_plan，而crontab_app中的API都是针对列表，所以包上中括号成为列表
    sentimentAnalysis([monitor_plan])
    generateWordCloud([monitor_plan])
    pid = os.getpid()

    # 杀死任务进程，防止显存不释放
    process = psutil.Process(pid)
    process.terminate()