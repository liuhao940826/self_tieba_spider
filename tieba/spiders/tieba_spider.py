# -*- coding: utf-8 -*-
import os
import sys
from datetime import date, datetime
import datetime as dealDate

import pandas as pd
import scrapy
import json

from dateutil.relativedelta import relativedelta

from tieba.items import ThreadItem, PostItem, CommentItem, TiebaInfo, TiebaAccountInfo
from . import helper
import time

class TiebaSpider(scrapy.Spider):
    name = "baidu_tieba"
    cur_page = 1    #modified by pipelines (open_spider)
    end_page = 9999
    filter = None
    see_lz = False

    const_active_tieba = 'active_tieba'

    def __init__(self):
        scrapy.Spider.__init__(self)

        config_path = os.path.join(os.path.split(
            os.path.realpath(__file__))[0], '../../config.json')

        if not os.path.isfile(config_path):
            sys.exit(u'当前路径：%s 不存在配置文件config.json' %
                     (os.path.split(os.path.realpath(__file__))[0] + os.sep))
        with open(config_path) as f:
            config = json.loads(f.read())

        #是否全量获取
        fullCollection = config['FULLCOLLECT_FLAG']
        print("setting的fullCollection的值:{}".format(fullCollection))
        isTrue = fullCollection == str(True)

        if isTrue:
            self.since_date = str(date.today() - relativedelta(months=+3))
        else:
            self.since_date = '1900-1-1'
        self.since_date += " 00:00:00"

    def parse(self, response): #forum parser

        pre_titleName =response.xpath('//head/title//text()').extract_first()
        print("head中的贴吧名:",pre_titleName)
        titleName = pre_titleName.split('-')[0]
        #贴吧name就是贴吧id
        titleId = pre_titleName.split('-')[0]
        #关注数
        card_menNum = response.xpath('//span[contains(@class, "card_numLabel")]')
        #发帖数
        card_infoNum = response.xpath('//span[contains(@class, "card_infoNum")]')
        print("关注数:{}".format(card_menNum))
        print("发帖数:{}".format(card_infoNum))
        tiebaInfo =TiebaInfo()
        #贴吧id 暂时跳转都是fw=贴吧名
        tiebaInfo['outId'] = titleId
        #贴吧名和贴吧id是一致的
        tiebaInfo['tiebaName'] = titleName
        #关注数
        tiebaInfo['accountCount'] = card_menNum
        #帖子数
        tiebaInfo['postCount'] = card_infoNum

        manager_groups = response.xpath('//ul[contains(@class, "manager_groups aside_media_horizontal")]')
        print("管理员列表:{}".format(manager_groups))

        noreferrer_name_list = manager_groups.xpath('//a[@rel="noreferrer"]/@title').extract()
        print("吧主名字集合数据:{}".format(noreferrer_name_list))
        noreferrer_name_str = ",".join(noreferrer_name_list)
        #暂时先获取对应的名字
        tiebaInfo["managerIds"] = noreferrer_name_str
        yield tiebaInfo

        thread_list = response.xpath('//li[contains(@class, "j_thread_list")]')

        thread_author_list = response.xpath('//span[contains(@class, "tb_icon_author")]')
        #这个时间不行格式有问题
        # thread_create_time_list = response.xpath('//span[contains(@class, "is_show_create_time")]')


        for index, sel in enumerate(thread_list):
            data = json.loads(sel.xpath('@data-field').extract_first())

            user_data = thread_author_list.xpath('@data-field').extract()[index]

            # create_time = thread_create_time_list.extract()[index]

            print("用户id信息:{}".format(user_data))
            print("用户名字:{}".format(data['author_name']))
            print("用户id的data类型:{}".format(type(user_data)))

            author_data = json.loads(user_data)
            item = ThreadItem()
            # 贴吧账号id
            item['tiebaAccountId'] = author_data['user_id']
            #外部内容id 帖子id
            item['outContentId'] = data['id']
            # 贴吧名就是贴吧id
            item['tiebaInfoId'] = titleName
            # item['reply_num'] = data['reply_num']
            # item['good'] = data['is_good']
            print("用户详情页跳转标识:{}".format(data['author_portrait']))

            # if not item['good']:
            #     item['good'] = False
            from scrapy.shell import inspect_response
            # 内容
            item['content'] = sel.xpath('.//div[contains(@class, "threadlist_title")]/a/@title').extract_first()
            if self.filter and not self.filter(item["id"], item["title"], item['author'], item['reply_num'], item['good']):
                continue
            print("filter的值:{}".format(filter))
            #filter过滤掉的帖子及其回复均不存入数据库

            url = 'http://tieba.baidu.com/p/%d' % data['id']
            if self.see_lz:
                url += '?see_lz=1'
            #处理帖子发帖时间请求的
            yield scrapy.Request(url, callback=self.parse_thread_time, cb_kwargs=dict(item))

            #获取对应的详情页信息放入楼层处理
            # print("调用用户详情.......................")
            # yield scrapy.Request(url, callback=self.parse_user_detail, meta=meta)

        next_page = response.xpath('//a[@class="next pagination-item "]/@href')
        self.cur_page += 1
        if next_page:
            if self.cur_page <= self.end_page:
                yield self.make_requests_from_url('http:'+next_page.extract_first())

    #使用cb_kwargs
    def parse_thread_time(self, response, tiebaAccountId, outContentId, tiebaInfoId, content):

        print("1楼的传递参数: tiebaAccountId:{},outContentId:{} tiebaInfoId:{}"
              .format(tiebaAccountId, outContentId, tiebaInfoId))

        item = ThreadItem()
        # 贴吧账号id
        item['tiebaAccountId'] = tiebaAccountId
        # 外部内容id 帖子id
        item['outContentId'] = outContentId
        # 贴吧名就是贴吧id
        item['tiebaInfoId'] = tiebaInfoId
        #内容
        item['content'] = content

        #请求一次url详情页url地址获取第一个楼层就是帖子本身
        first_floor = response.xpath("//div[contains(@class, 'l_post')]").extract_first()

        first_data_field = response.xpath("//div[contains(@class, 'l_post')]/@data-field").extract_first()
        # print("first_floor的信息:{}".format(first_floor))
        #获取第一个信息来获取发帖时间
        # first_data_field = first_floor.xpath("//div/@data-field").extract_first()
        print("first_data_field的信息:{}".format(first_data_field))
        first_floor_data = json.loads(first_data_field)
        #初始化时间
        thread_time = None

        if 'date' in first_floor_data['content'].keys():
            thread_time = first_floor_data['content']['date']
            item['publishTime'] =thread_time
            # 只有以前的帖子, data-field里面才有date
        else:
            thread_time = first_floor.xpath(".//span[@class='tail-info']") \
                .re_first(r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}')

            item['publishTime'] = thread_time

        print("时间:{}".format(thread_time))
        #时间格式处理
        thread_time = self.dealTime(thread_time)

        created_at = datetime.strptime(
            thread_time, "%Y-%m-%d %H:%M:%S")
        since_date = datetime.strptime(
            self.since_date, "%Y-%m-%d %H:%M:%S")

        send_Flag = created_at < since_date

        if send_Flag:
            item['isSend'] = False
        else:
            item['isSend'] = True
        yield item

        #帖子不发送了 楼层没必要获取了
        if send_Flag:
            # yield item
            meta = {'threadId': outContentId, 'tiebaInfoId': tiebaInfoId, 'page': 1,
                    self.const_active_tieba: {tiebaInfoId: 0}}

            print("跳转帖子对应的楼层详情页URL:{}".format(response.url))
            yield scrapy.Request(response.url, callback=self.parse_post, meta=meta)



    def parse_post(self, response):
        meta = response.meta
        has_comment = False
        # total_commont_floor_num = 0

        # 递归调用时候增加总数 放在另一个服务里面去统计
        # if meta.has_key('total_commont_floor_num'):
        #     print("已经有了统计的总数:{}".format(meta['total_commont_floor_num']))
        #     total_commont_floor_num = meta['total_commont_floor_num']


        floor_list = response.xpath("//div[contains(@class, 'l_post')]")
        #vip 用户会有 vip_red 在class 中 这边用contains
        # post_floor_userinfo_list = response.xpath('//a[contains(@class, "p_author_name")]//@href')


        # print("楼层用户的集合的长度:{}".format(len(post_floor_userinfo_list)))

        for index, floor in enumerate(floor_list):
            if not helper.is_ad(floor):
                # total_commont_floor_num  +=1
                data = json.loads(floor.xpath("@data-field").extract_first())
                item = PostItem()

                # 楼层用户名
                # item['author'] = data['author']['user_name']
                # 楼层用户id
                item['tiebaAccountId'] = data['author']['user_id']
                # 具体楼层评论数 用来处理楼中楼信息
                content = floor.xpath(".//div[contains(@class,'j_d_post_content')]").extract_first()
                # 以前的帖子, data-field里面没有content
                item['content'] = helper.parse_content(content)
                #楼层id
                item['outContentId'] = data['content']['post_id']
                #贴吧id
                item['tiebaInfoId'] = meta['tiebaInfoId']
                # TODO 获取用户逇跳转链接 可以直接拿去扒数据
                # print("获取:{}".format(user_detail_href))
                # item['user_detail_href'] = user_detail_href
                #以前的帖子, data-field里面没有 threadId
                item['threadId'] = meta['threadId']
                #楼层信息
                # item['floor'] = data['content']['post_no']

                post_time = None
                #只有以前的帖子, data-field里面才有date
                if 'date' in data['content'].keys():
                    post_time = data['content']['date']
                    item['publishTime'] =post_time
                    #只有以前的帖子, data-field里面才有date
                else:
                    post_time = floor.xpath(".//span[@class='tail-info']")\
                    .re_first(r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}')
                    item['publishTime'] =post_time

                # 时间格式处理
                post_time = self.dealTime(post_time)

                created_at = datetime.strptime(
                    post_time, "%Y-%m-%d %H:%M:%S")
                since_date = datetime.strptime(
                    self.since_date, "%Y-%m-%d %H:%M:%S")

                if created_at < since_date:
                    item['isSend'] = False
                else:
                    item['isSend'] = True
                #处理评论
                item['comment_num'] = data['content']['comment_num']
                if item['comment_num'] > 0:
                    has_comment = True
                yield item

                user_detail_href ="https://tieba.baidu.com/home/main?id=" + data['author']['portrait']
                #请求用户详情页
                yield scrapy.Request(user_detail_href, callback=self.parse_user_detail, meta=meta, cb_kwargs=dict(item))

        # meta['total_commont_floor_num'] = total_commont_floor_num
        if has_comment:
            url = "http://tieba.baidu.com/p/totalComment?tid=%d&fid=1&pn=%d" % (meta['threadId'], meta['page'])
            if self.see_lz:
                url += '&see_lz=1'
            yield scrapy.Request(url, callback=self.parse_comment, meta = meta)
        next_page = response.xpath(u".//ul[@class='l_posts_num']//a[text()='下一页']/@href")
        if next_page:
            meta['page'] += 1
            url = response.urljoin(next_page.extract_first())
            yield scrapy.Request(url, callback=self.parse_post, meta = meta)

    def parse_comment(self, response):
        comment_list = json.loads(response.body.decode('utf8'))['data']['comment_list']

        meta = response.meta

        # total_commont_floor_num = 0

        # 递归调用时候增加总数
        # if meta.has_key('total_commont_floor_num'):
        #     print("已经有了统计的总数:{}".format(meta['total_commont_floor_num']))
        #     total_commont_floor_num = meta['total_commont_floor_num']

        for value in comment_list.values():
            comments = value['comment_info']
            for comment in comments:
                #添加总共的评论
                # total_commont_floor_num+=1
                item = CommentItem()
                # 评论的贴吧账号id
                item['tiebaAccountId'] = comment['user_id']
                # 内容
                item['content'] = helper.parse_content(comment['content'])
                #外部id
                item['outContentId'] = comment['comment_id']
                #贴吧id 就是贴吧名字
                item['tiebaInfoId'] = meta['tiebaInfoId']
                # 发布时间
                item['publishTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment['now_time']))
                # item['author'] = comment['username']
                # 帖子id
                item['threadId'] = meta['threadId']
                #楼中楼的 对应的 楼层id
                item['postId'] = comment['post_id']
                yield item

    #用户详情页
    def parse_user_detail(self, response, tiebaAccountId):
        print("用户详情回调被执行....................")
        meta = response.meta

        item = TiebaAccountInfo()
        # 用户id
        item['outAccountId'] = tiebaAccountId
        # 获取用户名
        username = response.xpath('.//span[@class="userinfo_username "]/text()').extract()
        print("获取用户名:{}".format(username))
        # 用户名称
        item['nickname'] = username
        #url
        item['tiebaUrl'] = response.url

        # 获取对应的详情页信息
        userinfo_userdata = response.xpath('.//div[contains(@class, "userinfo_userdata")]//span/text()').extract()
        print("获取用户详情信息:{}".format(userinfo_userdata))

        # user_name = userinfo_userdata[0].split(":")[-1]
        # tieba_age = userinfo_userdata[2].split(":")[-1]
        # post_num = userinfo_userdata[-2].split(":")[-1]
        #这边位置更改过
        tieba_age = userinfo_userdata[1].split(":")[-1]
        post_num = userinfo_userdata[-1].split(":")[-1]

        # print("获取用户的用户名:{}".format(userinfo_userdata[0].split(":")[-1]))
        print("用户的发帖数量:{}".format(post_num))
        print("用户的吧龄:{}".format(tieba_age))

        item['postCount'] = post_num
        item['commentCount'] = post_num

        # 贴吧id
        item['tiebaOutId'] = meta['tiebaInfoId']


        # userinfo_userdata = response.xpath('.//div[contains(@class, "userinfo_userdata")]/span').extract()
        # print("获取用户详情信息:{}".format(userinfo_userdata))



        #这些暂时没用
        # post_time = response.xpath('.//div[contains(@class, "n_post_time")]/text()').extract()
        # print("获取用户帖子发布时间集合,和下面的对应:{}".format(post_time))
        # tieba_href = response.xpath('.//div[contains(@class, "thread_name")]//a/@href').extract()
        #
        # print("获取用户详情页帖子的跳转href:{}".format(tieba_href))
        #
        # tieba_title_list = response.xpath(
        #     './/div[contains(@class, "thread_name")]//a[@class="n_name"]//text()').extract()
        #
        # print("获取用户详情页帖子后缀的贴吧的名字:{}:{}".format(tieba_title_list))

        # 如果可以看到的发帖的内容不为空的话就拼接活跃贴吧
        # if tieba_title_list is not None and len(tieba_title_list) > 0:
        #     for tieba_title in tieba_title_list:
        #         meta[self.const_active_tieba][tieba_title] = 0

        # 插入对应的用户外部信息

        yield item

    def dealTime(self,date_text):
        try:
            dealDate.datetime.strptime(date_text, '%Y-%m-%d %H:%M')
            return date_text + ':00'
        except ValueError:
            pass

        return date_text

