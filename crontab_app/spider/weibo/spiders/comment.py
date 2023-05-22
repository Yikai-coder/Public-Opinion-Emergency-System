from email.mime import base
import re

import scrapy
from ..custom_settings import custom_settings_for_comment_spider
from ..items import CommentItem
from lxml import etree
import time
from ..utils.util import extract_comment_content, time_fix


class CommentSpider(scrapy.Spider):
    name = "comment_spider"
    custom_settings = custom_settings_for_comment_spider
    base_url = "https://weibo.cn"
    def start_requests(self):
        # url = self.settings.get("URL")
        url = self.base_url+"/comment/"+self.settings.get("BID")
        yield scrapy.Request(
            url=url,
            callback=self.parse,
        )
    
    def parse(self, response):
        comment_nodes = response.xpath('//div[@class="c" and contains(@id,"C_")]')
        for comment_node in comment_nodes:
            comment_user_url = comment_node.xpath('.//a[contains(@href,"/u/")]/@href').extract_first()
            if not comment_user_url:
                continue
            comment_item = CommentItem()
            comment_item['crawl_time'] = int(time.time())
            comment_item['weibo_id'] = response.url.split('/')[-1].split('?')[0]
            comment_item['comment_user_id'] = re.search(r'/u/(\d+)', comment_user_url).group(1)
            comment_item['content'] = extract_comment_content(comment_node.extract())
            comment_item['_id'] = comment_node.xpath('./@id').extract_first()
            created_at_info = comment_node.xpath('.//span[@class="ct"]/text()').extract_first()
            like_num = comment_node.xpath('.//a[contains(text(),"赞[")]/text()').extract_first()
            comment_item['like_num'] = int(re.search('\d+', like_num).group())
            comment_item['comment_time'] = time_fix(created_at_info.split('\xa0')[0])
            comment_item['comment_place'] = created_at_info.split('\xa0')[-1].split("来自")[-1]

            yield comment_item

        next_url = response.xpath(
            '//a[contains(text(), "下页")]/@href').extract_first()
        if next_url:
            next_url = self.base_url + next_url
            yield scrapy.Request(url=next_url,
                                    callback=self.parse)



        