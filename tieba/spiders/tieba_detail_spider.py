# import json
#
# import scrapy
#
# from tieba.items import UserDetailInfo
#
#
# class mingyan(scrapy.Spider):  # 需要继承scrapy.Spider类
#
#     #内置配置覆盖全局 pipline
#     # custom_settings = {
#     #     'ITEM_PIPELINES': {
#     #         'mingyan2.pipelines.Mingyan4Pipeline': 100,
#     #     }
#     # }
#     start_urls = [  # 另外一种写法，无需定义start_requests方法
#         'http://tieba.baidu.com/home/main?id=tb.1.7365b6e9.hTnRrAQgTMyPopY9SrfOXw',
#     ]
#
#     name = "tieba_user_detail"  # 定义蜘蛛名
#
#     # def start_requests(self):  # 由此方法通过下面链接爬取页面
#     #
#     #     # 定义爬取的链接
#     #     urls = [
#     #         'http://lab.scrapyd.cn/page/1/',
#     #         'http://lab.scrapyd.cn/page/2/',
#     #     ]
#     #     for url in urls:
#     #         yield scrapy.Request(url=url, callback=self.parse)  # 爬取到的页面如何处理？提交给parse方法处理
#
#     def parse(self, response):
#         print("用户详情回调被执行....................")
#         meta = response.meta
#
#         userinfo_userdata = response.xpath('.//div[contains(@class, "userinfo_userdata")]/span').extract()
#
#         nick_name = response.xpath('.//span[@class="userinfo_username"]/text()').extract()
#
#         print("获取用户的昵称:{}".format(nick_name))
#         print("获取用户详情信息:{}".format(userinfo_userdata))
#
#         # 获取对应的详情页信息
#         userinfo_userdata = response.xpath('.//div[contains(@class, "userinfo_userdata")]//span/text()').extract()
#
#         print("获取用户详情信息:{}".format(userinfo_userdata))
#
#         # user_name = userinfo_userdata[0].split(":")[-1]
#         # tieba_age = userinfo_userdata[2].split(":")[-1]
#         # post_num = userinfo_userdata[-2].split(":")[-1]
#
#         tieba_age = userinfo_userdata[2].split(":")[-1]
#         post_num = userinfo_userdata[-1].split(":")[-1]
#
#         print("获取用户的用户名:{}".format(userinfo_userdata[0].split(":")[-1]))
#         print("用户的发帖数量:{}".format(post_num))
#         print("用户的吧龄:{}".format(tieba_age))
#
#         post_time = response.xpath('.//div[contains(@class, "n_post_time")]/text()').extract()
#         print("获取用户帖子发布时间集合:{}".format(post_time))
#         tieba_href = response.xpath('.//div[contains(@class, "thread_name")]//a/@href').extract()
#
#         print("获取用户详情页帖子的跳转href:{}".format(tieba_href))
#
#         tieba_title_list = response.xpath(
#             './/div[contains(@class, "thread_name")]//a[@class="n_name"]//text()').extract()
#
#         print("获取用户详情页帖子的名字:{}".format(tieba_title_list))
#
#         # 如果可以看到的发帖的内容不为空的话就拼接活跃贴吧
#         if tieba_title_list is not None and len(tieba_title_list) > 0:
#             for tieba_title in tieba_title_list:
#                 meta[self.const_active_tieba][tieba_title] = 0
#
#         # 插入对应的用户外部信息
#         item = UserDetailInfo()
#         # item['user_name'] = user_name
#         item['tieba_age'] = tieba_age
#         item['post_num'] = post_num
#         item_active_tieba = ",".join(meta[self.const_active_tieba])
#         print("item_active_tieba:的内容{}".format(item_active_tieba))
#         item['active_tieba'] = item_active_tieba
#         yield item
#
#
#     # 获取对应的详情页信息
#     # def parse_user_detail(self, response):
#     #
#     #
#     #
#     #     user_detail_commont_detail_url = 'https://tieba.baidu.com/'
#     #
#     #     # 调用到具体帖子的详情页
#     #     if tieba_href is not None and len(tieba_href) > 0:
#     #         yield scrapy.Request(user_detail_commont_detail_url + tieba_href, callback=self.parse_post, meta=meta)
