import os, sys
from celery import platforms
from scrapy.crawler import CrawlerProcess
from billiard import Process
from scrapy.utils.project import get_project_settings
import datetime
from scrapy.crawler import CrawlerProcess
from celery.utils.log import get_task_logger

from spider.weibo.spiders.keyword_search import KeyWordSearchSpider

logger = get_task_logger(__name__)

class CrawlerScript(Process):
        def __init__(self, spider, settings):
            Process.__init__(self)
            self.crawler = CrawlerProcess(settings)
            self.spider = spider

        def run(self):
            self.crawler.crawl(self.spider)
            self.crawler.start()

def run_search_spider(keyword_list:list=None, start_date:str=None, end_date:str=None, region:list=None, weibo_type:int=None, further_threshold:int=None):
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', "spider.weibo.settings")  # 需要设置环境变量让get_project_settings能够找到settings.py
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', "peos.settings")
    print("1")
    settings = get_project_settings()
    print("2")
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
    spider = KeyWordSearchSpider
    crawler = CrawlerScript(spider, settings)
    crawler.start()
    crawler.join()

sys.path.append("/home/li/data/repo/Weibo-Public-Opinion-System/peos/celery_tasks") 

platforms.C_FORCE_ROOT = True

def traceTopic():
    # monitor_plan = MonitorPlanItem.objects.get(id=monitor_plan_id) 
    run_search_spider(keyword_list=["#宝马mini#"], 
                      start_date=(datetime.datetime.now()-datetime.timedelta(days=7)).strftime('%Y-%m-%d'),
                      end_date=datetime.datetime.now().strftime('%Y-%m-%d')
    )
    return 0

if __name__=="__main__":
    traceTopic()