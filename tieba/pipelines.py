# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

import requests
from twisted.enterprise import adbapi
import pymysql
import pymysql.cursors
from six.moves.urllib.parse import quote
from tieba.items import ThreadItem, PostItem, CommentItem

class TiebaPipeline(object):
    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    def __init__(self, settings):
        # dbname = settings['MYSQL_DBNAME']
        tbname = settings['TIEBA_NAME']
        # if not dbname.strip():
        #     raise ValueError("No database name!")
        if not tbname.strip():
            raise ValueError("No tieba name!")

        self.settings = settings

        # self.dbpool = adbapi.ConnectionPool('pymysql',
        #     host=settings['MYSQL_HOST'],
        #     db=settings['MYSQL_DBNAME'],
        #     user=settings['MYSQL_USER'],
        #     passwd=settings['MYSQL_PASSWD'],
        #     charset='utf8mb4',
        #     cursorclass = pymysql.cursors.DictCursor,
        #     init_command = 'set foreign_key_checks=0' #异步容易冲突
        # )
        
    def open_spider(self, spider):
        spider.cur_page = begin_page = self.settings['BEGIN_PAGE']
        spider.end_page = self.settings['END_PAGE']
        spider.filter = self.settings['FILTER']
        spider.see_lz = self.settings['SEE_LZ']
        tbname = self.settings['TIEBA_NAME']
        if not isinstance(tbname, bytes):
            tbname = tbname.encode('utf8')
        start_url = "http://tieba.baidu.com/f?kw=%s&pn=%d" \
                %(quote(tbname), 50 * (begin_page - 1))
        if self.settings['GOOD_ONLY']:
            start_url += '&tab=good'
        
        spider.start_urls = [start_url]
        
    def close_spider(self, spider):
        self.settings['SIMPLE_LOG'].log(spider.cur_page - 1)
    
    def process_item(self, item, spider):
        _conditional_insert = {
            'tiebaInfo': self.send_tieba_Info,
            'thread': self.sendInfo,
            'post': self.sendInfo,
            'comment': self.sendInfo,
            # 放到另一个爬虫从用户的详情页去获取
            # 'outerInfo': self.user_outer_Info
        }
        #注释掉数据库操作
        # query = self.dbpool.runInteraction(_conditional_insert[item.name], item)
        # query.addErrback(self._handle_error, item, spider)
        return item

    def send_tieba_Info(self,tx, item):
        jsondata = json.dumps(item.__dict__)
        dataType = 4
        r = requests.post(
            "http://localhost:9005/social-api/inner/channel/tiebaConfig/revice?" + "dataType=" + str(dataType), None,
            jsondata)


    def send_thread(self, tx, item):
        jsondata = json.dumps(item.__dict__)
        dataType = 1
        r = requests.post(
            "http://localhost:9005/social-api/inner/channel/tiebaConfig/revice?" + "dataType=" + str(dataType), None,
            jsondata)

        return
        
    def insert_post(self, tx, item):
        jsondata = json.dumps(item.__dict__)
        dataType = 2
        r = requests.post(
            "http://localhost:9005/social-api/inner/channel/tiebaConfig/revice?" + "dataType=" + str(dataType), None,
            jsondata)
        return
    def insert_comment(self, tx, item):
        jsondata = json.dumps(item.__dict__)
        dataType = 3
        r = requests.post(
            "http://localhost:9005/social-api/inner/channel/tiebaConfig/revice?" + "dataType=" + str(dataType), None,
            jsondata)
        return
    # def user_outer_Info(self,tx,item):
    #     sql = "replace into user_outer_Info values(%s, %s,%s, %s, %s, %s)"
    #     params = (0, item['author_id'], item['author'], item['content'], item['time'], item['post_id'])
    #     tx.execute(sql, params)

    #错误处理方法
    def _handle_error(self, fail, item, spider):
        spider.logger.error('Insert to database error: %s \
        when dealing with item: %s' %(fail, item))
