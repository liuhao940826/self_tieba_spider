# -*- coding: utf-8 -*-
import pandas as pd
import scrapy
import json
from tieba.items import ThreadItem, PostItem, CommentItem, UserDetailInfo
from . import helper
import time

class TiebaSpider(scrapy.Spider):
    name = "tieba"
    cur_page = 1    #modified by pipelines (open_spider)
    end_page = 9999
    filter = None
    see_lz = False

    const_active_tieba = 'active_tieba'


    def parse(self, response): #forum parser

        pre_titleName =response.xpath('//head/title//text()').extract_first()
        print("head中的贴吧名:",pre_titleName)
        titleName=pre_titleName.split('-')[0]

        thread_list = response.xpath('//li[contains(@class, "j_thread_list")]')

        thread_author_list = response.xpath('//span[contains(@class, "tb_icon_author")]')

        fileName = '测试-日志.html'  # 爬取的内容存入文件，文件名为：作者-语录.txt

        f = open(fileName, "wb")  # 追加写入文件
        f.write(response.body)  # 写入名言内容
        f.close()  # 关闭文件操作

        for index, sel in enumerate(thread_list):
            data = json.loads(sel.xpath('@data-field').extract_first())

            user_data = thread_author_list.xpath('@data-field').extract()[index]

            print("用户id信息:{}".format(user_data))
            print("用户名字:{}".format(data['author_name']))
            print("用户id的data类型:{}".format(type(user_data)))

            author_data = json.loads(user_data)
            item = ThreadItem()
            item['id'] = data['id']
            item['author_id'] = author_data['user_id']
            item['tbName']=titleName
            item['author'] = data['author_name']
            item['reply_num'] = data['reply_num']
            item['good'] = data['is_good']
            print("用户详情页跳转标识:{}".format(data['author_portrait']))

            if not item['good']:
                item['good'] = False
            from scrapy.shell import inspect_response
            item['title'] = sel.xpath('.//div[contains(@class, "threadlist_title")]/a/@title').extract_first()
            if self.filter and not self.filter(item["id"], item["title"], item['author'], item['reply_num'], item['good']):
                continue
            #filter过滤掉的帖子及其回复均不存入数据库
            yield item
            meta = {'thread_id': data['id'], 'page': 1, self.const_active_tieba: {titleName: 0}}
            url = 'http://tieba.baidu.com/p/%d' % data['id']
            if self.see_lz:
                url += '?see_lz=1'
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
                item['id'] = data['content']['post_id']
                item['author'] = data['author']['user_name']
                item['author_id'] = data['author']['user_id']
                #获取用户逇跳转链接
                user_detail_href ="https://tieba.baidu.com" + post_floor_userinfo_list.extract()[index]
                print("获取:{}".format(user_detail_href))
                item['user_detail_href'] = user_detail_href
                #评论数
                item['comment_num'] = data['content']['comment_num']
                if item['comment_num'] > 0:
                    has_comment = True
                content = floor.xpath(".//div[contains(@class,'j_d_post_content')]").extract_first()
                #以前的帖子, data-field里面没有content
                item['content'] = helper.parse_content(content)
                #以前的帖子, data-field里面没有thread_id
                item['thread_id'] = meta['thread_id']
                item['floor'] = data['content']['post_no']
                #只有以前的帖子, data-field里面才有date
                if 'date' in data['content'].keys():
                    item['time'] = data['content']['date']
                    #只有以前的帖子, data-field里面才有date
                else:
                    item['time'] = floor.xpath(".//span[@class='tail-info']")\
                    .re_first(r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}')
                yield item
        # meta['total_commont_floor_num'] = total_commont_floor_num
        if has_comment:
            url = "http://tieba.baidu.com/p/totalComment?tid=%d&fid=1&pn=%d" % (meta['thread_id'], meta['page'])
            if self.see_lz:
                url += '&see_lz=1'
            yield scrapy.Request(url, callback = self.parse_comment, meta = meta)
        next_page = response.xpath(u".//ul[@class='l_posts_num']//a[text()='下一页']/@href")
        if next_page:
            meta['page'] += 1
            url = response.urljoin(next_page.extract_first())
            yield scrapy.Request(url, callback = self.parse_post, meta = meta)

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
                item['id'] = comment['comment_id']
                item['author_id'] = comment['user_id']
                item['author'] = comment['username']
                item['post_id'] = comment['post_id']
                item['content'] = helper.parse_content(comment['content'])
                item['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment['now_time']))
                yield item


