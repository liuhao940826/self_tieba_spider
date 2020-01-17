# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ThreadItem(scrapy.Item):
    name = 'thread'
    id = scrapy.Field()
    author_id = scrapy.Field()
    tbName = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    reply_num = scrapy.Field()
    good = scrapy.Field()
    
class PostItem(scrapy.Item):
    name = 'post'
    id = scrapy.Field()
    floor = scrapy.Field()
    user_detail_href = scrapy.Field()
    author_id = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    time = scrapy.Field()
    comment_num = scrapy.Field()
    thread_id = scrapy.Field()

class CommentItem(scrapy.Item):
    name = 'comment'
    id = scrapy.Field()
    author_id = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    time = scrapy.Field()
    post_id = scrapy.Field()

class UserDetailInfo(scrapy.Item):
    name ='outerInfo'
    id = scrapy.Field()
    channel_type = scrapy.Field()
    user_name = scrapy.Field()
    tieba_age = scrapy.Field()
    post_num = scrapy.Field()
    active_tieba = scrapy.Field()




