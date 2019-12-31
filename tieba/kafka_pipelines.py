# -*- coding: utf-8 -*-

# Scrapy
import json

from scrapy.utils.project import get_project_settings

# PyKafka
from pykafka import KafkaClient


class ScrapyProducerKafkaPipeline(object):

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
        self._client = KafkaClient(hosts=kafka_ip_port)
        topic = settings['KAFKA_TOPIC_NAME'].encode(encoding="UTF-8")
        print("kafka消费topic:",topic)

        # 初始化Producer 需要把topic name变成字节的形式
        self._producer = \
            self._client.topics[
                topic
            ].get_producer()

    '''
        每一个管道必须实现的功能
    '''
    def process_item(self, item, spider):
        """
        写数据到Kafka
        :param item:
        :param spider:
        :return:
        """
        if spider.name == "tieba":
            self._producer.produce(item)
            print("我发送消息了.......内容 %s",json.dumps(item))
            return item

    def close_spider(self, spider):
        """
        结束之后关闭Kafka
        :return:
        """
        if spider.name == "tieba":
            self._producer.stop()