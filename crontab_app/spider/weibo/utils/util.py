import sys
from datetime import datetime, timedelta
from urllib.parse import unquote

from crontab_app.spider.weibo.utils.region import region_dict
import re
# import datetime
import logging

logger = logging.getLogger("crontab_app.spider.utils")
def convert_weibo_type(weibo_type):
    """将微博类型转换成字符串"""
    if weibo_type == 0:
        return '&typeall=1'
    elif weibo_type == 1:
        return '&scope=ori'
    elif weibo_type == 2:
        return '&xsort=hot'
    elif weibo_type == 3:
        return '&atten=1'
    elif weibo_type == 4:
        return '&vip=1'
    elif weibo_type == 5:
        return '&category=4'
    elif weibo_type == 6:
        return '&viewpoint=1'
    return '&scope=ori'


def convert_contain_type(contain_type):
    """将包含类型转换成字符串"""
    if contain_type == 0:
        return '&suball=1'
    elif contain_type == 1:
        return '&haspic=1'
    elif contain_type == 2:
        return '&hasvideo=1'
    elif contain_type == 3:
        return '&hasmusic=1'
    elif contain_type == 4:
        return '&haslink=1'
    return '&suball=1'


def get_keyword_list(file_name):
    """获取文件中的关键词列表"""
    with open(file_name, 'rb') as f:
        try:
            lines = f.read().splitlines()
            lines = [line.decode('utf-8-sig') for line in lines]
        except UnicodeDecodeError:
            logger.error(u'%s文件应为utf-8编码，请先将文件编码转为utf-8再运行程序', file_name)
            sys.exit()
        keyword_list = []
        for line in lines:
            if line:
                keyword_list.append(line)
    return keyword_list


def get_regions(region):
    """根据区域筛选条件返回符合要求的region"""
    new_region = {}
    if region:
        for key in region:
            if region_dict.get(key):
                new_region[key] = region_dict[key]
    if not new_region:
        new_region = region_dict
    return new_region


def standardize_date(created_at):
    """标准化微博发布时间"""
    if "刚刚" in created_at:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    elif "秒" in created_at:
        second = created_at[:created_at.find(u"秒")]
        second = timedelta(seconds=int(second))
        created_at = (datetime.now() - second).strftime("%Y-%m-%d %H:%M")
    elif "分钟" in created_at:
        minute = created_at[:created_at.find(u"分钟")]
        minute = timedelta(minutes=int(minute))
        created_at = (datetime.now() - minute).strftime("%Y-%m-%d %H:%M")
    elif "小时" in created_at:
        hour = created_at[:created_at.find(u"小时")]
        hour = timedelta(hours=int(hour))
        created_at = (datetime.now() - hour).strftime("%Y-%m-%d %H:%M")
    elif "今天" in created_at:
        today = datetime.now().strftime('%Y-%m-%d')
        created_at = today + ' ' + created_at[2:]
    elif '年' not in created_at:
        year = datetime.now().strftime("%Y")
        month = created_at[:2]
        day = created_at[3:5]
        time = created_at[6:]
        created_at = year + '-' + month + '-' + day + ' ' + time
    else:
        year = created_at[:4]
        month = created_at[5:7]
        day = created_at[8:10]
        time = created_at[11:]
        created_at = year + '-' + month + '-' + day + ' ' + time
    return created_at


def str_to_time(text):
    """将字符串转换成时间类型"""
    result = datetime.strptime(text, '%Y-%m-%d')
    return result


def time_fix(time_string):
    now_time = datetime.now()
    if '分钟前' in time_string:
        minutes = re.search(r'^(\d+)分钟', time_string).group(1)
        created_at = now_time - timedelta(minutes=int(minutes))
        return created_at.strftime('%Y-%m-%d %H:%M')

    if '小时前' in time_string:
        minutes = re.search(r'^(\d+)小时', time_string).group(1)
        created_at = now_time - timedelta(hours=int(minutes))
        return created_at.strftime('%Y-%m-%d %H:%M')

    if '今天' in time_string:
        return time_string.replace('今天', now_time.strftime('%Y-%m-%d'))

    if '月' in time_string:
        time_string = time_string.replace('月', '-').replace('日', '')
        time_string = str(now_time.year) + '-' + time_string
        return time_string

    return time_string


keyword_re = re.compile('<span class="kt">|</span>|原图|<!-- 是否进行翻译 -->|<span class="cmt">|\[组图共.+张\]')
emoji_re = re.compile('<img alt="|" src=".*>')
white_space_re = re.compile('<br />')
div_re = re.compile('</div>|<div>')
image_re = re.compile('<img(.*?)/>|<span class="url-icon">')
url_re = re.compile('<a href=(.*?)>|</a>')


def extract_weibo_content(weibo_html):
    s = weibo_html
    if 'class="ctt">' in s:
        s = s.split('class="ctt">', maxsplit=1)[1]
    s = emoji_re.sub('', s)
    s = url_re.sub('', s)
    s = div_re.sub('', s)
    s = image_re.sub('', s)
    if '<span class="ct">' in s:
        s = s.split('<span class="ct">')[0]
    splits = s.split('赞[')
    if len(splits) == 2:
        s = splits[0]
    if len(splits) == 3:
        origin_text = splits[0]
        retweet_text = splits[1].split('转发理由:')[1]
        s = origin_text + '转发理由:' + retweet_text
    s = white_space_re.sub(' ', s)
    s = keyword_re.sub('', s)
    s = s.replace('\xa0', '')
    s = s.strip(':')
    s = s.strip()
    return s


def extract_comment_content(comment_html):
    s = comment_html
    if 'class="ctt">' in s:
        s = s.split('class="ctt">', maxsplit=1)[1]
    s = s.split('举报', maxsplit=1)[0]
    s = emoji_re.sub('', s)
    s = keyword_re.sub('', s)
    s = url_re.sub('', s)
    s = div_re.sub('', s)
    s = image_re.sub('', s)
    s = white_space_re.sub(' ', s)
    s = s.replace('\xa0', '')
    s = s.strip(':')
    s = s.strip()
    return s

def extract_repost_content(repost_html):
    s = repost_html
    if 'class="cc">' in s:
        s = s.split('<span class="cc">', maxsplit=1)[0]
    s = emoji_re.sub('', s)
    s = keyword_re.sub('', s)
    s = url_re.sub('', s)
    s = div_re.sub('', s)
    s = image_re.sub('', s)
    s = white_space_re.sub(' ', s)
    s = s.replace('\xa0', '')
    s = s.replace('<div class="c">', '')
    s = s.strip(':')
    s = s.strip()
    return s

def get_article_url(selector):
    """获取微博头条文章url"""
    article_url = ''
    text = selector.xpath('string(.)').extract_first().replace(
        '\u200b', '').replace('\ue627', '').replace('\n',
                                                    '').replace(' ', '')
    if text.startswith('发布了头条文章'):
        urls = selector.xpath('.//a')
        for url in urls:
            if url.xpath(
                    'i[@class="wbicon"]/text()').extract_first() == 'O':
                if url.xpath('@href').extract_first() and url.xpath(
                        '@href').extract_first().startswith('http://t.cn'):
                    article_url = url.xpath('@href').extract_first()
                break
    return article_url

def get_location(selector):
    """获取微博发布位置"""
    a_list = selector.xpath('.//a')
    location = ''
    for a in a_list:
        if a.xpath('./i[@class="wbicon"]') and a.xpath(
                './i[@class="wbicon"]/text()').extract_first() == '2':
            location = a.xpath('string(.)').extract_first()[1:]
            break
    return location

def get_at_users(selector):
    """获取微博中@的用户昵称"""
    a_list = selector.xpath('.//a')
    at_users = dict()
    at_list = []
    for a in a_list:
        if len(unquote(a.xpath('@href').extract_first())) > 14 and len(
                a.xpath('string(.)').extract_first()) > 1:
            if unquote(a.xpath('@href').extract_first())[14:] == a.xpath(
                    'string(.)').extract_first()[1:]:
                at_user = a.xpath('string(.)').extract_first()[1:]
                if at_user not in at_list:
                    at_list.append(at_user)
    if at_list:
        for user in at_user:
            at_users.update({len(at_user)+1:user})
    return at_users

def get_topics(selector):
    """获取参与的微博话题"""
    a_list = selector.xpath('.//a')
    topics = dict()
    topic_list = []
    for a in a_list:
        text = a.xpath('string(.)').extract_first()
        if len(text) > 2 and text[0] == '#' and text[-1] == '#':
            if text[1:-1] not in topic_list:
                topic_list.append(text[1:-1])
    if topic_list:
        for topic in topic_list:
            topics.update({len(topics)+1: topic})
    return topics
