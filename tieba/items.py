# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TiebaInfo(scrapy.Item):
    name = 'tiebaInfo'
    outId = scrapy.Field() #贴吧id 目前就是贴吧名
    tiebaName = scrapy.Field()  #贴吧名
    accountCount = scrapy.Field() #关联账户数
    postCount = scrapy.Field()    #帖子数
    managerIds = scrapy.Field()   #管理员名字

class TiebaAccountInfo(scrapy.Item):
    name = 'tiebaAccountInfo'
    outAccountId = scrapy.Field() #贴吧账号id
    nickname = scrapy.Field()     #用户昵称
    tiebaUrl = scrapy.Field()      #用户详情页跳转url
    postCount = scrapy.Field()    #发帖数
    commentCount = scrapy.Field() #评论数
    tiebaOutId  =scrapy.Field() #贴吧的id 在插入用户信息的时候做关联

class ThreadItem(scrapy.Item):
    name = 'thread'
    # 贴吧账号id
    tiebaAccountId = scrapy.Field()
    #内容
    content = scrapy.Field()
    #外部内容id
    outContentId = scrapy.Field()
    #贴吧id 就是贴吧名
    tiebaInfoId = scrapy.Field()
    #发布时间
    publishTime = scrapy.Field()
    #是否采集
    isSend = scrapy.Field()


    # reply_num = scrapy.Field()
    # good = scrapy.Field()
    
class PostItem(scrapy.Item):
    name = 'post'
    # 贴吧账号id
    tiebaAccountId = scrapy.Field()
    # 内容
    content = scrapy.Field()
    # 外部内容id
    outContentId = scrapy.Field()
    # 贴吧id 就是贴吧名
    tiebaInfoId = scrapy.Field()
    #发布时间
    publishTime = scrapy.Field()
    #帖子id
    threadId = scrapy.Field()
    # 是否采集
    isSend = scrapy.Field()

class CommentItem(scrapy.Item):
    name = 'comment'
    # 贴吧账号id
    tiebaAccountId = scrapy.Field()
    # 内容
    content = scrapy.Field()
    # 外部内容id
    outContentId = scrapy.Field()
    # 贴吧id 就是贴吧名
    tiebaInfoId = scrapy.Field()
    # 发布时间
    publishTime = scrapy.Field()
    # 帖子id
    threadId = scrapy.Field()
    # 楼层id 放在关联id里面
    postId = scrapy.Field()
    # 是否采集
    isSend = scrapy.Field()




