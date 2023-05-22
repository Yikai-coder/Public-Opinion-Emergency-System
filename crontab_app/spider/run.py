import csv
import sys
#被引用模块所在的路径
# sys.path.append("/home/li/data/repo/Weibo-Public-Opinion-System/spider") 
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from weibo.spiders.user import UserSpider
from weibo.spiders.keyword_search import KeyWordSearchSpider
from weibo.spiders.hot_search import HotSearchSpider
from weibo.spiders.url import URLSpider
from weibo.spiders.comment import CommentSpider

def run_search_spider(keyword_list:list=None, start_date:str=None, end_date:str=None, region:list=None, weibo_type:int=None, further_threshold:int=None):
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

    process = CrawlerProcess(settings)

    process.crawl(KeyWordSearchSpider)
    process.start() # the script will block here until the crawling is finished

def run_hotsearch_spider():
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    process.crawl(HotSearchSpider)
    process.start() # the script will block here until the crawling is finished

def run_url_spider():
    settings = get_project_settings()
    urls = []
    # with open('/home/li/data/repo/Weibo-Public-Opinion-System/spider/结果文件/热搜/热搜.csv') as f:
    #     reader = csv.reader(f)
    #     header_row = next(reader)
    #     for row in reader:
    #         urls.append(row[-1])
    settings.set("URL", "https://s.weibo.com/weibo?q=%23%E7%9F%B3%E5%AE%B6%E5%BA%84%E7%96%AB%E6%83%85%E9%98%B2%E6%8E%A7%23")
    process = CrawlerProcess(settings)

    process.crawl(URLSpider)
    process.start() # the script will block here until the crawling is finished

def run_comment_spider(bid):
    settings = get_project_settings()
    settings.set('BID', bid)
    process = CrawlerProcess(settings)

    process.crawl(CommentSpider)
    process.start() # the script will block here until the crawling is finished

def run_user_spider(uid):
    settings = get_project_settings()
    settings.set('UID', uid)
    process = CrawlerProcess(settings)

    process.crawl(UserSpider)
    process.start() # the script will block here until the crawling is finished

if __name__ == "__main__":
    # run_search_spider(keyword_list=['唐山打人案'], start_date='2022-06-10', end_date='2022-10-26', weibo_type=0, further_threshold=40)
    # run_hotsearch_spider()
    run_url_spider()
    # run_comment_spider("M6vFG7TOd")
    # run_user_spider(6012229852)