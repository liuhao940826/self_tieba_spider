# -*- coding: utf-8 -*-

BOT_NAME = 'tieba'

SPIDER_MODULES = ['tieba.spiders']
NEWSPIDER_MODULE = 'tieba.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html

ITEM_PIPELINES = {
    # 'tieba.kafka_producer_pipelines.ScrapyProducerKafkaPipeline': 300,
    # 'tieba.kafka_consumer_pipelines.ScrapyConsumerKafkaPipeline': 300
    'tieba.pipelines.TiebaPipeline': 300,
}

LOG_LEVEL = 'WARNING'

COMMANDS_MODULE = 'tieba.commands'

# KAFKA_SERVER = '192.168.1.152:9092'
# KAFKA_TOPIC_NAME = 'TIEBA'
