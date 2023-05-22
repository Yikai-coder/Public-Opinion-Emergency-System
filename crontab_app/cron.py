import sys
#被引用模块所在的路径
sys.path.append("/home/li/data/repo/Weibo-Public-Opinion-System/peos") 
sys.path.append("/home/li/data/repo/Weibo-Public-Opinion-System/peos/crontab_app") 
sys.path.append("/home/li/data/repo/Weibo-Public-Opinion-System/peos/crontab_app/spider")
sys.path.append("/home/li/data/repo/Weibo-Public-Opinion-System/peos/crontab_app/sentiment/bert")
from multiprocessing import Process
import datetime
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spider.weibo.spiders.hot_search import HotSearchSpider
from spider.weibo.spiders.keyword_search import KeyWordSearchSpider
from spider.weibo.spiders.url import URLSpider
from hotsearch_analysis.models import HotSearchItem
from monitor_plan.models import MonitorPlanItem
from sentiment.bert.test import test
from SA.models import situationAwareness
from word_cloud.wordcloud import generate_wordcloud_meta
from public.utils import check_connection

import logging
logger = logging.getLogger("crontab_app")

def hotsearchSituationAwareness():
    # 首先检查MySQL连接是否仍然有效
    # if not is_connection_usable():
    #     connection.close()
    check_connection()
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', "spider.weibo.settings")  # 需要设置环境变量让get_project_settings能够找到settings.py
    settings = get_project_settings()
    logger.warning("Start crawl Hotsearch")
    crawlHotsearch(settings)
    logger.warning("finish crawl hotsearchs")
    # # 然后爬取热搜对应的微博
    hotsearchs = HotSearchItem.objects.order_by("-time")[:50]
    logger.warning(hotsearchs)
    # 爬微博前先更新cookies
    logger.warning("start update cookies")
    updateSettingsCookies()
    logger.warning("finish update cookies")
    logger.warning("Start crawl weibos")
    crwalWeibo(hotsearchs, settings)
    logger.warning("Finish crawl weibo")
    logger.warning("Start sentimentAnalysis")
    new_hotsearchs = HotSearchItem.objects.order_by("-time")[:50]  # 重新获取queryset从而得到更新后带有read_count的hotsearch
    # 对每条热搜及其对应的微博进行情感分析，得到每条热搜的情感分布
    sentimentAnalysis(new_hotsearchs)
    # 对每条热搜统计词频，生成词云元数据
    # logger.warning("Start generateWordCloud")
    generateWordCloud(new_hotsearchs)
    # 进行态势评分
    logger.warning("Start hotsearchAnalysis")
    for hotsearch in new_hotsearchs:
        logger.warning("title:%s, read_count:%d", hotsearch.title, hotsearch.read_count)
    hotsearchAnalysis(new_hotsearchs)
    
def monitorPlanFollow():
    """
    跟进所有的monitor_plan，包括：
    1. 爬取过去1天内该方案对应的微博
    2. 对新爬取的微博进行情感分析，然后更新监控方案的情感分布和词云
    """
    # 首先检查MySQL连接是否仍然有效
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', "spider.weibo.settings")  # 需要设置环境变量让get_project_settings能够找到settings.py
    items = MonitorPlanItem.objects.all()
    n_procs_parallel = 1
    logger.warning("start update cookies")
    updateSettingsCookies()
    logger.warning("finish update cookies")
    check_connection()
    def run_search_spider(monitor_plan_item, type):
        settings = get_project_settings()
        settings.set('KEYWORD_LIST', monitor_plan_item.keywords['keywords'])
        settings.set("END_DATE", datetime.datetime.now().strftime('%Y-%m-%d'))
        settings.set('START_DATE', (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
        settings.set('MONITOR_PLAN', monitor_plan_item)
        settings.set("WEIBO_TYPE", type)
        process = CrawlerProcess(settings)
        process.crawl(KeyWordSearchSpider)
        process.start() # the script will block here until the crawling is finished
    logger.warning("start crawl weibo")
    for type in (5, 2, 1): # 要搜索的微博类型，0代表搜索全部微博，1代表搜索全部原创微博，2代表热门微博，3代表关注人微博，4代表认证用户微博，5代表媒体微博，6代表观点微博
        for n_monitor_plan in range(0, len(items), n_procs_parallel):
            procs = []
            for n_proc in range(n_procs_parallel):
                p = Process(target=run_search_spider, args=(items[n_monitor_plan+n_proc], type, ))
                p.start()
                procs.append(p)
            for p in procs:
                p.join()
    check_connection()
    logger.warning("start sentimentAnalysis")
    sentimentAnalysis(items)
    logger.warning("start generateWordCloud")
    generateWordCloud(items) 

def updateSettingsCookies():
    """
    微博的cookie只有一天，需要每天登录获取新的cookie，
    又因为微博的安全验证机制，导致登陆必须扫码，代码无法通过模拟的方式实现，
    所以使用selenium模拟chrome浏览器行为，将一个chrome浏览器常驻在系统中，
    并登录weibo.com，每天定时刷新该网页获取cookie
    """
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9527")
    browser = webdriver.Chrome(options=options)

    browser.refresh()
    cookies = browser.get_cookies()
    cookie_list = []
    for item in cookies:
        cookie = item['name']+'='+item['value']
        cookie_list.append(cookie)
    cookie_str = ';'.join(cookie_list)
    def _updateSettingsCookies(filename, cookie_str):
        try:
            with open(filename, 'r') as f1, open(filename+".new", 'w') as f2:
                for line in f1:
                    f2.write(re.sub("(?<=[\', \"]cookie[\', \"]:[\', \"])[\s\S]+(?=[\', \"],)", cookie_str, line))
            os.remove(filename)
            os.rename(filename+".new", filename)
        except Exception as e:
            logger.warning("catch exception in updateSettingsCookies "+str(e))
    _updateSettingsCookies("/home/li/data/repo/Weibo-Public-Opinion-System/peos/crontab_app/spider/weibo/settings.py", cookie_str)
    _updateSettingsCookies("/home/li/data/repo/Weibo-Public-Opinion-System/peos/celery_tasks/spider/weibo/settings.py", cookie_str)
    return
    
def hotsearchAnalysis(hotsearchs):  
    """
    对热搜进行态势感知，使用熵值法进行态势评分

    Args:
        hotsearchs (list): 热搜列表
    """
    sa_values = situationAwareness(hotsearchs.values_list("read_count", "discussion_count", "degree", "negative_sentiment_portion"))
    for hotsearch, val in zip(hotsearchs, sa_values):
        hotsearch.sa_value = val
        hotsearch.save()
    return

def crawlHotsearch(settings):
    """
    scrapy爬取热搜榜

    Args:
        settings (obj): scrapy的settigns对象，保存了cookie等信息
    """
    def run_hotsearch_spider():
        process = CrawlerProcess(settings)
        # 首先爬取热搜，将热搜信息存入数据库 
        process.crawl(HotSearchSpider)
        process.start() # the script will block here until the crawling is finished
    p = Process(target=run_hotsearch_spider, args=())
    p.start()
    p.join()
    
def crwalWeibo(hotsearchs, settings):
    """
    爬取热搜对应的50条左右微博用于后续分析

    Args:
        hotsearchs (list): 热搜列表
        settings (obj): scrapy的settigns对象，保存了cookie等信息
    """
    n_procs_parallel = 1
    def run_url_spider(url, type, id):
        # check_connection()
        settings.set("URL", url)
        settings.set("WEIBO_TYPE", type)
        settings.set("hotsearch_id", id)
        process = CrawlerProcess(settings)
        process.crawl(URLSpider)
        process.start() # the script will block here until the crawling is finished
    for type in [5, 2, 1]: # 要搜索的微博类型，0代表搜索全部微博，1代表搜索全部原创微博，2代表热门微博，3代表关注人微博，4代表认证用户微博，5代表媒体微博，6代表观点微博
        for n_hotsearch in range(0, len(hotsearchs), n_procs_parallel):
            procs = []
            for n_proc in range(n_procs_parallel):
                p = Process(target=run_url_spider, args=(hotsearchs[n_hotsearch+n_proc].url, type, hotsearchs[n_hotsearch+n_proc].id))
                p.start()
                procs.append(p)
            for p in procs:
                p.join()

def sentimentAnalysis(hotsearchs):
    """
    分析每条热搜对应的微博，从而获得每条热搜的情感分布

    Args:
        hotsearchs (list): 热搜列表
    """
    for hotsearch in hotsearchs:
        weibos = hotsearch.weiboitem_set.all().filter(sentiment='') # 对已经进行过情感分析的微博跳过，避免爆显存
        # weibos = hotsearch.weiboitem_set.all()
        if hotsearch.sentiment_distribution is None or not isinstance(hotsearch.sentiment_distribution, dict):
            hotsearch.sentiment_distribution = {}
        text = [weibo.text for weibo in weibos]
        if text == []:
            if not str(datetime.date.today()) in hotsearch.sentiment_distribution.keys():
                hotsearch.sentiment_distribution[str(datetime.date.today())] = {
                    "angry": 0,
                    "sad": 0 ,
                    "fear": 0,
                    "neutral": 0,
                    "happy": 0,
                    "surprise": 0
                }
                hotsearch.save()
            continue
        ans = test(text)
        num_to_label = [
            "angry",
            "sad",
            "fear",
            "neutral",
            "happy",
            "surprise"
        ]
        for weibo, sentiment in zip(weibos, ans):
            weibo.sentiment = num_to_label[sentiment]
            weibo.save()
        sentiment_distribution = {
            "angry": 0,
            "sad": 0 ,
            "fear": 0,
            "neutral": 0,
            "happy": 0,
            "surprise": 0
        }
        negative_sentiment = 0
        for i in range(len(ans)):
            sentiment_distribution[num_to_label[ans[i]]] += 1 
            if num_to_label[ans[i]] in ("angry", "sad", "fear"):
                negative_sentiment+=1
        if not str(datetime.date.today()) in hotsearch.sentiment_distribution:
            hotsearch.sentiment_distribution[str(datetime.date.today())] = sentiment_distribution
        else:
            ori_sentiment = hotsearch.sentiment_distribution[str(datetime.date.today())]
            for key in ori_sentiment.keys():
                ori_sentiment[key] += sentiment_distribution[key]
            hotsearch.sentiment_distribution[str(datetime.date.today())] = ori_sentiment
        hotsearch.negative_sentiment_portion = negative_sentiment / len(weibos)
        def calculate_total_sentiment(sentiment_distribution):
            total_sentiment = {}
            for date in sentiment_distribution.keys():
                for sentiment in sentiment_distribution[date].keys():
                    if sentiment in total_sentiment:
                        total_sentiment[sentiment] += sentiment_distribution[date][sentiment]
                    else:
                        total_sentiment[sentiment] = sentiment_distribution[date][sentiment]
            return total_sentiment
        total_sentiment = calculate_total_sentiment(hotsearch.sentiment_distribution)
        hotsearch.dominant_sentiment = max(total_sentiment, key=lambda sentiment: total_sentiment[sentiment])
        hotsearch.save()

def generateWordCloud(hotsearchs):
    """
    使用热搜对应的微博生成词云

    Args:
        hotsearchs (list): 热搜列表
    """
    for hotsearch in hotsearchs:
        weibos = hotsearch.weiboitem_set.all()
        text = []
        for weibo in weibos:
            text.append(weibo.text)
        if text == []:
            continue
        hotsearch.word_cloud = generate_wordcloud_meta(text)
        hotsearch.save()
