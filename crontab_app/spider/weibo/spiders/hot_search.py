from operator import itemgetter
import os
import re
import sys
from datetime import datetime, timedelta
from urllib.parse import unquote
import time
import pytz
import re
import scrapy
import weibo.utils.util as util
from scrapy.exceptions import CloseSpider
from weibo.items import HotSearchItem, WeiboItem
from ..custom_settings import custom_settings_for_hotsearch_spider

class HotSearchSpider(scrapy.Spider):
    name = "hotsearch_spider"
    url = 'https://s.weibo.com/top/summary?cate=realtimehot'
    custom_settings = custom_settings_for_hotsearch_spider
    
    def start_requests(self):
        yield scrapy.Request(self.url, callback=self.parse)

    def parse(self, response):
        tz = pytz.timezone('Asia/Shanghai')  # 设定时间到东八区，scrapy内会修改时区导致时间不准确
        now_time = datetime.fromtimestamp(int(time.time()), tz).strftime('%Y-%m-%d %H:%M:%S')
        titles = response.xpath('//tr[position()>1]')
        for title in titles:
            item = HotSearchItem()
            rank_list = re.findall("\d+\.?\d*",
                                    title.xpath('.//td[contains(@class,"td-01")]/text()').extract()[0].strip()
            )
            # 微博热搜榜上存在没有排名的热搜广告，需要排除
            if rank_list == []:
                continue
            item['rank'] = rank_list[0]
            item['title'] = title.xpath(
                './/td[@class="td-02"]/a/text()').extract()[0].strip()
            # 热搜榜上的热度数据有的时候会有类似“综艺 102390”的出现形式
            item['degree'] = re.findall("\d+\.?\d*", 
                                    title.xpath(
                                    './/td[@class="td-02"]/span/text()').extract()[0].strip())[0]

            item['time'] = now_time
            item['url'] = 'https://s.weibo.com/' + title.xpath(
                './/td[@class="td-02"]/a/@href').extract()[0].strip()
            # print(item)
            # 在爬取话题阅读数等信息
            # yield scrapy.Request(url=item['url'], callback=self.parse_details, meta={'item': item})
            yield item
        
    # def parse_details(self, response):
    #     item = response.meta['item']
    #     data_row = response.xpath('//div[@class="total"]')
    #     try:
    #         item['read_count'] = self.str2value(data_row.xpath(".//span[1]/text()").extract_first().split("今日阅读")[-1])
    #         item['discussion_count'] = self.str2value(data_row.xpath(".//span[2]/text()").extract_first().split("今日讨论")[-1])
    #     except AttributeError:
    #         print(response)
    #     yield item

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
        