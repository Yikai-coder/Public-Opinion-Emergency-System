# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from hotsearch_analysis import models
from scrapy_djangoitem import DjangoItem

class WeiboItem(DjangoItem):
    # define the fields for your item here like:
    # id = scrapy.Field()
    # bid = scrapy.Field()
    # user_id = scrapy.Field()
    # screen_name = scrapy.Field()
    # text = scrapy.Field()
    # article_url = scrapy.Field()
    # location = scrapy.Field()
    # at_users = scrapy.Field()
    # topics = scrapy.Field()
    # reposts_count = scrapy.Field()
    # comments_count = scrapy.Field()
    # attitudes_count = scrapy.Field()
    # created_at = scrapy.Field()
    # source = scrapy.Field()
    # pics = scrapy.Field()
    # video_url = scrapy.Field()
    # retweet_id = scrapy.Field()
    django_model = models.WeiboItem

class HotSearchItem(DjangoItem):
    # define the fields for your item here like:
    # rank = scrapy.Field()
    # title = scrapy.Field()
    # degree = scrapy.Field()
    # time = scrapy.Field()
    # url = scrapy.Field()
    django_model = models.HotSearchItem 

class CommentItem(scrapy.Item):
    """
    微博评论信息
    """
    _id = scrapy.Field()
    comment_user_id = scrapy.Field()  # 评论用户的id
    content = scrapy.Field()  # 评论的内容
    weibo_id = scrapy.Field()  # 评论的微博的id
    comment_time = scrapy.Field()  # 评论发表时间
    like_num = scrapy.Field()  # 点赞数
    crawl_time = scrapy.Field()  # 抓取时间戳
    comment_place = scrapy.Field() # 评论地点

class UserItem(scrapy.Item):
    """ User Information"""
    _id = scrapy.Field()  # 用户ID
    nick_name = scrapy.Field()  # 昵称
    gender = scrapy.Field()  # 性别
    province = scrapy.Field()  # 所在省
    city = scrapy.Field()  # 所在城市
    brief_introduction = scrapy.Field()  # 简介
    birthday = scrapy.Field()  # 生日
    tweets_num = scrapy.Field()  # 微博数
    follows_num = scrapy.Field()  # 关注数
    fans_num = scrapy.Field()  # 粉丝数
    sex_orientation = scrapy.Field()  # 性取向
    sentiment = scrapy.Field()  # 感情状况
    vip_level = scrapy.Field()  # 会员等级
    authentication = scrapy.Field()  # 认证
    education = scrapy.Field()  # 学习经历
    work = scrapy.Field()  # 工作经历
    person_url = scrapy.Field()  # 首页链接
    labels = scrapy.Field()  # 标签
    crawl_time = scrapy.Field()  # 抓取时间戳
