# -*- coding: utf-8 -*-
import pandas as pd
import scrapy
import json
from tieba.items import ThreadItem, PostItem, CommentItem, UserDetailInfo, TiebaInfo
from . import helper
import time

class TiebaSpider(scrapy.Spider):
    name = "baidu_tieba"
    cur_page = 1    #modified by pipelines (open_spider)
    end_page = 9999
    filter = None
    see_lz = False

    const_active_tieba = 'active_tieba'

    # @classmethod
    # def from_crawler(cls, crawler):
    #     # This method is used by Scrapy to create your spiders.
    #     s = cls()
    #
    #     machine_name = crawler.settings.(
    #         'MACHINE_NAME', '')
    #
    #     return s


    def parse(self, response): #forum parser

        fullcollectFlag = self.settings["FULLCOLLECT_FLAG"]
        print("采集标识的类型:{}".format(type(fullcollectFlag)))
        print("采集数据的值:{}".format(fullcollectFlag))

        pre_titleName =response.xpath('//head/title//text()').extract_first()
        print("head中的贴吧名:",pre_titleName)
        titleName=pre_titleName.split('-')[0]
        #贴吧name就是贴吧id
        titleId = pre_titleName.split('-')[0]
        #关注数
        card_menNum = response.xpath('//span[contains(@class, "card_numLabel")]')
        #发帖数
        card_infoNum = response.xpath('//span[contains(@class, "card_infoNum")]')
        print("关注数:{}".format(card_menNum))
        print("发帖数:{}".format(card_infoNum))
        tiebaInfo =TiebaInfo();
        #贴吧id 暂时跳转都是fw=贴吧名
        tiebaInfo['outId']=titleId
        #贴吧名
        tiebaInfo['name']=titleName
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

            # yield item
            meta = {'threadId': data['id'], 'tiebaInfoId' : titleName ,'page': 1, self.const_active_tieba: {titleName: 0}}

            print("跳转对应的详情页URL:{}".format(url))
            yield scrapy.Request(url, callback=self.parse_post,  meta=meta)
            #获取对应的详情页信息
            # print("调用用户详情.......................")
            # yield scrapy.Request(url, callback=self.parse_user_detail, meta=meta)

        next_page = response.xpath('//a[@class="next pagination-item "]/@href')
        self.cur_page += 1
        if next_page:
            if self.cur_page <= self.end_page:
                yield self.make_requests_from_url('http:'+next_page.extract_first())

    #使用cb_kwargs
    def parse_thread_time(self,response,tiebaAccountId,outContentId,tiebaInfoId,content):

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
        #获取第一个信息来获取发帖时间
        first_floor_data = json.loads(first_floor.xpath("@data-field").extract_first())
        if 'date' in first_floor_data['content'].keys():
            item['time'] = first_floor_data['content']['date']
            # 只有以前的帖子, data-field里面才有date
        else:
            item['time'] = first_floor.xpath(".//span[@class='tail-info']") \
                .re_first(r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}')
        yield item

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
        post_floor_userinfo_list = response.xpath('//a[contains(@class, "p_author_name")]//@href')

        print("楼层数组的长度:{}".format(len(floor_list)))
        print("楼层用户的集合的长度:{}".format(len(post_floor_userinfo_list)))

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
                # user_detail_href ="https://tieba.baidu.com" + post_floor_userinfo_list.extract()[index]
                # print("获取:{}".format(user_detail_href))
                # item['user_detail_href'] = user_detail_href
                #以前的帖子, data-field里面没有 threadId
                item['threadId'] = meta['threadId']
                #楼层信息
                # item['floor'] = data['content']['post_no']
                #只有以前的帖子, data-field里面才有date
                if 'date' in data['content'].keys():
                    item['publishTime'] = data['content']['date']
                    #只有以前的帖子, data-field里面才有date
                else:
                    item['publishTime'] = floor.xpath(".//span[@class='tail-info']")\
                    .re_first(r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}')

                #处理评论
                item['comment_num'] = data['content']['comment_num']
                if item['comment_num'] > 0:
                    has_comment = True
                yield item
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


