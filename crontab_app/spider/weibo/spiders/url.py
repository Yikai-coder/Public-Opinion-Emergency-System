import re
from datetime import datetime, timedelta

import scrapy
import spider.weibo.utils.util as util
from scrapy.exceptions import CloseSpider
from django.utils import timezone

from weibo.items import WeiboItem
from hotsearch_analysis.models import HotSearchItem
from ..custom_settings import custom_settings_for_url_spider
import logging
logger = logging.getLogger("crontab_app.spider.url")

class URLSpider(scrapy.Spider):
    name = 'url'
    allowed_domains = ['weibo.com']
    base_url = 'https://s.weibo.com'
    custom_settings = custom_settings_for_url_spider

    def start_requests(self):
        url = self.settings.get("URL")
        self.weibo_type = util.convert_weibo_type(self.settings.get('WEIBO_TYPE'))
        url += self.weibo_type
        logger.debug(url)
        yield scrapy.Request(
            url=url,
            callback=self.parse,
        )
        
    def parse(self, response):
        base_url = response.meta.get('base_url')
        keyword = response.meta.get('keyword')
        province = response.meta.get('province')
        is_empty = response.xpath(
            '//div[@class="card card-no-result s-pt20b40"]')
        page_count = len(response.xpath('//ul[@class="s-scroll"]/li'))
        if self.weibo_type=="&scope=ori":
            self.parse_hotsearch_details(response)
        if is_empty:
            logger.warning('当前页面搜索结果为空, url:%s', str(response.url))
        elif page_count < self.settings.get("FURTHER_THRESHOLD"):
            # 解析当前页面
            for weibo in self.parse_weibo(response):
                # self.check_environment()
                yield weibo
            next_url = response.xpath(
                '//a[@class="next"]/@href').extract_first()
            if next_url:
                next_url = self.base_url + next_url
                yield scrapy.Request(url=next_url,
                                     callback=self.parse_page,
                                     meta={'keyword': keyword})
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=3)
            while start_date <= end_date:
                start_str = start_date.strftime('%Y-%m-%d') + '-0'
                start_date = start_date + timedelta(days=1)
                end_str = start_date.strftime('%Y-%m-%d') + '-0'
                url = self.base_url + str(self.settings['WEIBO_TYPE'])
                url += str(self.settings['CONTAIN_TYPE'])
                url += '&timescope=custom:{}:{}&page=1'.format(
                    start_str, end_str)
                # 获取一天的搜索结果
                yield scrapy.Request(url=url,
                                     callback=self.parse_by_day,
                                     meta={
                                         'base_url': base_url,
                                         'keyword': keyword,
                                         'province': province,
                                         'date': start_str[:-2]
                                     })

    def parse_by_day(self, response):
        """以天为单位筛选"""
        base_url = response.meta.get('base_url')
        keyword = response.meta.get('keyword')
        province = response.meta.get('province')
        is_empty = response.xpath(
            '//div[@class="card card-no-result s-pt20b40"]')
        date = response.meta.get('date')
        page_count = len(response.xpath('//ul[@class="s-scroll"]/li'))
        if is_empty:
            logger.warning('当前页面搜索结果为空, url:%s', response.url)
        elif page_count < self.further_threshold:
            # 解析当前页面
            for weibo in self.parse_weibo(response):
                # self.check_environment()
                yield weibo
            next_url = response.xpath(
                '//a[@class="next"]/@href').extract_first()
            if next_url:
                next_url = self.base_url + next_url
                yield scrapy.Request(url=next_url,
                                     callback=self.parse_page,
                                     meta={'keyword': keyword})
        else:
            start_date_str = date + '-0'
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d-%H')
            for i in range(1, 25):
                start_str = start_date.strftime('%Y-%m-%d-X%H').replace(
                    'X0', 'X').replace('X', '')
                start_date = start_date + timedelta(hours=1)
                end_str = start_date.strftime('%Y-%m-%d-X%H').replace(
                    'X0', 'X').replace('X', '')
                url = base_url + self.weibo_type
                url += self.contain_type
                url += '&timescope=custom:{}:{}&page=1'.format(
                    start_str, end_str)
                # 获取一小时的搜索结果
                yield scrapy.Request(url=url,
                                     callback=self.parse_by_hour_province
                                     if province else self.parse_by_hour,
                                     meta={
                                         'base_url': base_url,
                                         'keyword': keyword,
                                         'province': province,
                                         'start_time': start_str,
                                         'end_time': end_str
                                     })

    def parse_by_hour(self, response):
        """以小时为单位筛选"""
        keyword = response.meta.get('keyword')
        is_empty = response.xpath(
            '//div[@class="card card-no-result s-pt20b40"]')
        start_time = response.meta.get('start_time')
        end_time = response.meta.get('end_time')
        page_count = len(response.xpath('//ul[@class="s-scroll"]/li'))
        if is_empty:
            logger.warning('当前页面搜索结果为空, url:%s', response.url)
        elif page_count < self.further_threshold:
            # 解析当前页面
            for weibo in self.parse_weibo(response):
                # self.check_environment()
                yield weibo
            next_url = response.xpath(
                '//a[@class="next"]/@href').extract_first()
            if next_url:
                next_url = self.base_url + next_url
                yield scrapy.Request(url=next_url,
                                     callback=self.parse_page,
                                     meta={'keyword': keyword})
        else:
            for region in self.regions.values():
                url = ('https://s.weibo.com/weibo?q={}&region=custom:{}:1000'
                       ).format(keyword, region['code'])
                url += self.weibo_type
                url += self.contain_type
                url += '&timescope=custom:{}:{}&page=1'.format(
                    start_time, end_time)
                # 获取一小时一个省的搜索结果
                yield scrapy.Request(url=url,
                                     callback=self.parse_by_hour_province,
                                     meta={
                                         'keyword': keyword,
                                         'start_time': start_time,
                                         'end_time': end_time,
                                         'province': region
                                     })

    def parse_by_hour_province(self, response):
        """以小时和直辖市/省为单位筛选"""
        keyword = response.meta.get('keyword')
        is_empty = response.xpath(
            '//div[@class="card card-no-result s-pt20b40"]')
        start_time = response.meta.get('start_time')
        end_time = response.meta.get('end_time')
        province = response.meta.get('province')
        page_count = len(response.xpath('//ul[@class="s-scroll"]/li'))
        if is_empty:
            logger.warning('当前页面搜索结果为空, url:%s', response.url)
        elif page_count < self.further_threshold:
            # 解析当前页面
            for weibo in self.parse_weibo(response):
                # self.check_environment()
                yield weibo
            next_url = response.xpath(
                '//a[@class="next"]/@href').extract_first()
            if next_url:
                next_url = self.base_url + next_url
                yield scrapy.Request(url=next_url,
                                     callback=self.parse_page,
                                     meta={'keyword': keyword})
        else:
            for city in province['city'].values():
                url = ('https://s.weibo.com/weibo?q={}&region=custom:{}:{}'
                       ).format(keyword, province['code'], city)
                url += self.weibo_type
                url += self.contain_type
                url += '&timescope=custom:{}:{}&page=1'.format(
                    start_time, end_time)
                # 获取一小时一个城市的搜索结果
                yield scrapy.Request(url=url,
                                     callback=self.parse_page,
                                     meta={
                                         'keyword': keyword,
                                         'start_time': start_time,
                                         'end_time': end_time,
                                         'province': province,
                                         'city': city
                                     })

    def parse_page(self, response):
        """解析一页搜索结果的信息"""
        keyword = response.meta.get('keyword')
        is_empty = response.xpath(
            '//div[@class="card card-no-result s-pt20b40"]')
        cnt = 0
        if is_empty:
            logger.warning('当前页面搜索结果为空, url:%s', response.url)
        else:
            for weibo in self.parse_weibo(response):
                # self.check_environment()
                cnt+=1
                if cnt >= 50:
                    return
                yield weibo
            next_url = response.xpath(
                '//a[@class="next"]/@href').extract_first()
            if next_url:
                next_url = self.base_url + next_url
                yield scrapy.Request(url=next_url,
                                     callback=self.parse_page,
                                     meta={'keyword': keyword})



    def parse_weibo(self, response):
        """解析网页中的微博信息"""
        # self.parse_hotsearch_details(response)
        keyword = response.meta.get('keyword')
        for sel in response.xpath("//div[@class='card-wrap']"):
            info = sel.xpath(
                "div[@class='card']/div[@class='card-feed']/div[@class='content']/div[@class='info']"
            )
            if info:
                weibo = WeiboItem()
                type_num = self.settings.get("WEIBO_TYPE")
                weibo['type'] = "media" if type_num==5 else "hot" if type_num==2 else ""
                weibo['mid'] = sel.xpath('@mid').extract_first()
                weibo['bid'] = sel.xpath(
                    './/div[@class="from"]/a[1]/@href').extract_first(
                    ).split('/')[-1].split('?')[0]
                weibo['user_id'] = info[0].xpath(
                    'div[2]/a/@href').extract_first().split('?')[0].split(
                        '/')[-1]
                weibo['nick_name'] = info[0].xpath(
                    'div[2]/a/@nick-name').extract_first()
                txt_sel = sel.xpath('.//p[@class="txt"]')[0]
                retweet_sel = sel.xpath('.//div[@class="card-comment"]')
                retweet_txt_sel = ''
                if retweet_sel and retweet_sel[0].xpath('.//p[@class="txt"]'):
                    retweet_txt_sel = retweet_sel[0].xpath(
                        './/p[@class="txt"]')[0]
                content_full = sel.xpath(
                    './/p[@node-type="feed_list_content_full"]')
                is_long_weibo = False
                is_long_retweet = False
                if content_full:
                    if not retweet_sel:
                        txt_sel = content_full[0]
                        is_long_weibo = True
                    elif len(content_full) == 2:
                        txt_sel = content_full[0]
                        retweet_txt_sel = content_full[1]
                        is_long_weibo = True
                        is_long_retweet = True
                    elif retweet_sel[0].xpath(
                            './/p[@node-type="feed_list_content_full"]'):
                        retweet_txt_sel = retweet_sel[0].xpath(
                            './/p[@node-type="feed_list_content_full"]')[0]
                        is_long_retweet = True
                    else:
                        txt_sel = content_full[0]
                        is_long_weibo = True
                weibo['text'] = txt_sel.xpath(
                    'string(.)').extract_first().replace('\u200b', '').replace(
                        '\ue627', '')
                weibo['article_url'] = util.get_article_url(txt_sel)
                weibo['location'] = util.get_location(txt_sel)
                if weibo['location']:
                    weibo['text'] = weibo['text'].replace(
                        '2' + weibo['location'], '')
                weibo['text'] = weibo['text'][2:].replace(' ', '')
                if is_long_weibo:
                    weibo['text'] = weibo['text'][:-4]
                weibo['at_users'] = util.get_at_users(txt_sel)
                weibo['topics'] = util.get_topics(txt_sel)
                reposts_count = sel.xpath(
                    './/a[@action-type="feed_list_forward"]/text()').extract()
                reposts_count = "".join(reposts_count)
                try:
                    reposts_count = re.findall(r'\d+.*', reposts_count)
                except TypeError:
                    logger.error(
                        "无法解析转发按钮，可能是 1) 网页布局有改动 2) cookie无效或已过期。\n"
                        "请在 https://github.com/dataabc/weibo-search 查看文档，以解决问题，"
                    )
                    raise CloseSpider()
                weibo['reposts_count'] = reposts_count[
                    0] if reposts_count else '0'
                comments_count = sel.xpath(
                    './/a[@action-type="feed_list_comment"]/text()'
                ).extract_first()
                comments_count = re.findall(r'\d+.*', str(comments_count))
                weibo['comments_count'] = comments_count[
                    0] if comments_count else '0'
                attitudes_count = sel.xpath(
                    '(.//span[@class="woo-like-count"])[last()]/text()').extract_first()
                attitudes_count = re.findall(r'\d+.*', attitudes_count)
                weibo['attitudes_count'] = attitudes_count[
                    0] if attitudes_count else '0'
                created_at = sel.xpath(
                    './/div[@class="from"]/a[1]/text()').extract_first(
                    ).replace(' ', '').replace('\n', '').split('前')[0]
                created_at = created_at[:created_at.find("转赞")] if "转赞" in created_at else created_at
                weibo['created_at'] = util.standardize_date(created_at)
                source = sel.xpath('.//p[@class="from"]/a[2]/text()'
                                   ).extract_first()
                weibo['source'] = source if source else ''
                pics = dict()
                is_exist_pic = sel.xpath(
                    './/div[@class="media media-piclist"]')
                if is_exist_pic:
                    pics_list = is_exist_pic[0].xpath('ul[1]/li/img/@src').extract()
                    pics_list = [pic[8:] for pic in pics]
                    pics_list = [
                        re.sub(r'/.*?/', '/large/', pic, 1) for pic in pics
                    ]
                    pics_list = ['https://' + pic for pic in pics]
                    for url in pics_list:
                        pics.update({len(pics)+1:url})
                video_url = ''
                is_exist_video = sel.xpath(
                    './/div[@class="thumbnail"]//video-player').extract_first()
                if is_exist_video:
                    video_url = re.findall(r'src:\'(.*?)\'', is_exist_video)[0]
                    video_url = video_url.replace('&amp;', '&')
                    video_url = 'http:' + video_url
                if not retweet_sel:
                    weibo['pics'] = pics
                    weibo['video_url'] = video_url
                else:
                    weibo['pics'] = None
                    weibo['video_url'] = ''
                weibo['retweet_id'] = ''
                if retweet_sel and retweet_sel[0].xpath(
                        './/div[@node-type="feed_list_forwardContent"]/a[1]'):
                    retweet = WeiboItem()
                    retweet['mid'] = retweet_sel[0].xpath(
                        './/a[@action-type="feed_list_like"]/@action-data'
                    ).extract_first()[4:]
                    retweet['bid'] = retweet_sel[0].xpath(
                        './/p[@class="from"]/a/@href').extract_first().split(
                            '/')[-1].split('?')[0]
                    info = retweet_sel[0].xpath(
                        './/div[@node-type="feed_list_forwardContent"]/a[1]'
                    )[0]
                    retweet['user_id'] = info.xpath(
                        '@href').extract_first().split('/')[-1]
                    retweet['nick_name'] = info.xpath(
                        '@nick-name').extract_first()
                    retweet['text'] = retweet_txt_sel.xpath(
                        'string(.)').extract_first().replace('\u200b',
                                                             '').replace(
                                                                 '\ue627', '')
                    retweet['article_url'] = util.get_article_url(
                        retweet_txt_sel)
                    retweet['location'] = util.get_location(retweet_txt_sel)
                    if retweet['location']:
                        retweet['text'] = retweet['text'].replace(
                            '2' + retweet['location'], '')
                    retweet['text'] = retweet['text'][2:].replace(' ', '')
                    if is_long_retweet:
                        retweet['text'] = retweet['text'][:-4]
                    retweet['at_users'] = util.get_at_users(retweet_txt_sel)
                    retweet['topics'] = util.get_topics(retweet_txt_sel)
                    reposts_count = retweet_sel[0].xpath(
                        './/ul[@class="act s-fr"]/li[1]/a[1]/text()'
                    ).extract_first()
                    reposts_count = re.findall(r'\d+.*', reposts_count)
                    retweet['reposts_count'] = reposts_count[
                        0] if reposts_count else '0'
                    comments_count = retweet_sel[0].xpath(
                        './/ul[@class="act s-fr"]/li[2]/a[1]/text()'
                    ).extract_first()
                    comments_count = re.findall(r'\d+.*', comments_count)
                    retweet['comments_count'] = comments_count[
                        0] if comments_count else '0'
                    attitudes_count = retweet_sel[0].xpath(
                        './/a[@class="woo-box-flex woo-box-alignCenter woo-box-justifyCenter"]//span[@class="woo-like-count"]/text()'
                    ).extract_first()
                    attitudes_count = re.findall(r'\d+.*', attitudes_count)
                    retweet['attitudes_count'] = attitudes_count[
                        0] if attitudes_count else '0'
                    created_at = retweet_sel[0].xpath(
                        './/p[@class="from"]/a[1]/text()').extract_first(
                        ).replace(' ', '').replace('\n', '').split('前')[0]
                    retweet['created_at'] = util.standardize_date(created_at)
                    source = retweet_sel[0].xpath(
                        './/p[@class="from"]/a[2]/text()').extract_first()
                    retweet['source'] = source if source else ''
                    retweet['pics'] = pics
                    retweet['video_url'] = video_url
                    retweet['retweet_id'] = ''
                    yield {"item": retweet, "hotsearch_id": self.settings.get("hotsearch_id")}
                    weibo['retweet_id'] = retweet['mid']
                yield {"item": weibo, "hotsearch_id": self.settings.get("hotsearch_id")}

    def parse_hotsearch_details(self, response):
        hotsearch = HotSearchItem.objects.get(id=self.settings.get("hotsearch_id"))
        data_row = response.xpath('//div[@class="total"]')
        logger.warning("Get data_row:%s", data_row)
        try:
            hotsearch.read_count = self.str2value(data_row.xpath(".//span[1]/text()").extract_first().split("今日阅读")[-1])
            hotsearch.discussion_count = self.str2value(data_row.xpath(".//span[2]/text()").extract_first().split("今日讨论")[-1])
        except AttributeError:
            logger.error("catch AttributeError when get read_count")
        hotsearch.save()
        hotsearch = HotSearchItem.objects.get(id=self.settings.get("hotsearch_id"))
        logger.warning("After reload, title:%s, read_count:%d", hotsearch.title, hotsearch.read_count)
        return
        
    def str2value(self, valueStr):
        valueStr = str(valueStr)
        idxOfYi = valueStr.find('亿')
        idxOfWan = valueStr.find('万')
        if idxOfYi != -1 and idxOfWan != -1:
            return int(float(valueStr[:idxOfYi])*1e8 + float(valueStr[idxOfYi+1:idxOfWan])*1e4)
        elif idxOfYi != -1 and idxOfWan == -1:
            return int(float(valueStr[:idxOfYi])*1e8)
        elif idxOfYi == -1 and idxOfWan != -1:
            return int(float(valueStr[idxOfYi+1:idxOfWan])*1e4)
        elif idxOfYi == -1 and idxOfWan == -1:
            return float(valueStr)