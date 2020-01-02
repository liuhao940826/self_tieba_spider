# -*- coding: utf-8 -*-

# Scrapy
import json

from scrapy.utils.project import get_project_settings
# PyKafka
from kafka import KafkaProducer
import json
import time




class ScrapyProducerKafkaPipeline(object):

    _producer = None

    def __init__(self):
        # 判断下配置里面个给的是啥
        # 1. 如果长度等于1, list只有一个数据, 如果是字符肯定大于1
        # 2. 否则, 判断类型是否是list, 是的话用 逗号分隔
        # 3. 否则就是一个字符串
        settings = get_project_settings()

        print("管道中读取到的setting内容:",settings)
        kafka_ip_port = settings['KAFKA_SERVER']

        print("kafka的ip端口:",kafka_ip_port)

        if len(kafka_ip_port) == 1:
            kafka_ip_port = kafka_ip_port[0]
        else:
            if isinstance(kafka_ip_port, list):
                kafka_ip_port = ",".join(kafka_ip_port)
            else:
                kafka_ip_port = kafka_ip_port

        # 初始化client
        self.producer = KafkaProducer(bootstrap_servers=kafka_ip_port)

    '''
        每一个管道必须实现的功能
    '''
    def process_item(self, item, spider):

        print("开始解析对应的item内容.............")

        if spider.name == "tieba":
            #获取setting内容
            settings = get_project_settings()
            self.log('管道中读取到的setting内容: %s' % (settings))
            #获取topic内容
            topic = settings['KAFKA_TOPIC_NAME'].encode(encoding="UTF-8")
            #发送消息
            self.producer.send(topic, item)
            self.producer.flush()
            self.log('kafka发送内容: %s' % (json.dumps(item)))
            return item

    def close_spider(self, spider):
        """
        结束之后关闭Kafka
        :return:
        """
        if spider.name == "tieba":
            # self.producer.close()
            pass

    def log(str):
        t = time.strftime(r"%Y-%m-%d_%H-%M-%S", time.localtime())
        print("[%s]%s" % (t, str))


