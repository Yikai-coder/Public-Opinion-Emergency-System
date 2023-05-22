# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath('.')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'peos.settings'    # 项目名.settings
import django
django.setup()

BOT_NAME = 'celery_spider'
SPIDER_MODULES = ['celery_tasks.spider.weibo.spiders']
NEWSPIDER_MODULE = 'celery_tasks.spider.weibo.spiders'
COOKIES_ENABLED = False
TELNETCONSOLE_ENABLED = False
ROBOTSTXT_OBEY = False
LOG_LEVEL = 'ERROR'
# 访问完一个页面再访问下一个时需要等待的时间，默认为10秒
DOWNLOAD_DELAY = 10
DEFAULT_REQUEST_HEADERS = {
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language':
    'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
    'cookie':"YOUR_OWN_WEIBO_COOKIE",
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76',
    
    # 'User-Agent': 'Baiduspider+(+http://www.baidu.com/search/spider.htm)'
}
ITEM_PIPELINES = {
    'celery_tasks.spider.weibo.pipelines.KeyWordPipeline':300
}
CLOSESPIDER_TIMEOUT = 1800
# 要搜索的微博类型，0代表搜索全部微博，1代表搜索全部原创微博，2代表热门微博，3代表关注人微博，4代表认证用户微博，5代表媒体微博，6代表观点微博
WEIBO_TYPE = 0
# 筛选结果微博中必需包含的内容，0代表不筛选，获取全部微博，1代表搜索包含图片的微博，2代表包含视频的微博，3代表包含音乐的微博，4代表包含短链接的微博
CONTAIN_TYPE = 0
# 筛选微博的发布地区，精确到省或直辖市，值不应包含“省”或“市”等字，如想筛选北京市的微博请用“北京”而不是“北京市”，想要筛选安徽省的微博请用“安徽”而不是“安徽省”，可以写多个地区，
# 具体支持的地名见region.py文件，注意只支持省或直辖市的名字，省下面的市名及直辖市下面的区县名不支持，不筛选请用“全部”
REGION = ['全部']
# 建议数值大小设置在40到50之间。
FURTHER_THRESHOLD = 46
# 图片文件存储路径
IMAGES_STORE = './'
# 视频文件存储路径
FILES_STORE = './'