# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


class TiebaSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    '''
        如果存在，则调用该类方法以从中创建中间件实例Crawler。
        它必须返回中间件的新实例。搜寻器对象提供对所有Scrapy核心组件（如设置和信号）的访问；它是中间件访问它们并将其功能连接到Scrapy中的一种方式。
        参数：	搜寻器（Crawler对象）–使用此中间件的搜寻器
    '''
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    '''
        对于通过蜘蛛中间件并进入蜘蛛进行处理的每个响应，都会调用此方法。
        process_spider_input()应该返回None或引发异常。
        如果返回None，则Scrapy将继续处理此响应，并执行所有其他中间件，直到最终将响应交给蜘蛛进行处理。
        如果引发异常，Scrapy不会费心调用任何其他Spider中间件，process_spider_input()并且会在存在错误时调用请求errback，
        否则它将启动process_spider_exception() 链。errback的输出在另一个方向上被链回以process_spider_output()进行处理，
        或者 process_spider_exception()如果它引发了异常。
        参数：	
        响应（Response对象）–正在处理的响应
        蜘蛛（Spider对象）–此响应旨在的蜘蛛
    '''
    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    '''
        处理完响应后，将使用Spider从返回的结果中调用此方法。
        process_spider_output()必须返回Request，dict或Item 对象的可迭代 对象。
        参数：	
        响应（Response对象）–从蜘蛛生成此输出的响应
        结果（可迭代的Request，字典或Item对象）–蜘蛛返回的结果
        蜘蛛（Spider对象）–正在处理其结果的蜘蛛
    '''
    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i


    '''
    当蜘蛛或process_spider_output() 方法（来自先前的蜘蛛中间件）引发异常时，将调用此方法。

    process_spider_exception()应该返回，None或Request字典或 Item对象的可迭代值。
    
    如果返回None，则Scrapy将继续处理此异常，process_spider_exception()并在以下中间件组件中执行其他任何异常，
    直到没有剩余中间件组件且异常到达引擎为止（记录并丢弃该异常）。
    
    如果返回一个可迭代的process_spider_output()管道，则从下一个蜘蛛中间件开始，管道将启动，
    并且不会process_spider_exception()调用其他任何中间件 。
    
    参数：	
    响应（Response对象）–引发异常时正在处理的响应
    异常（Exception对象）–引发的异常
    蜘蛛（Spider对象）–引发异常的蜘蛛 
    '''
    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    '''
    0.15版中的新功能。
    
    该方法与Spider的启动请求一起调用，并且与该process_spider_output()方法类似，但它没有关联的响应，并且必须仅返回请求（不返回项目）。
    
    它接收（在start_requests参数中）可迭代的Request对象，并且必须返回另一个可迭代对象。
    
    注
    '''

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
