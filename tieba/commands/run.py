import scrapy.commands.crawl as crawl
from scrapy.crawler import CrawlerRunner
from scrapy.exceptions import UsageError
from scrapy.commands import ScrapyCommand
import config
import filter
from tieba.spiders.tieba_spider import TiebaSpider


class Command(crawl.Command):
    def syntax(self):
        return "<tieba_name> <database_name>"

    def short_desc(self):
        return "Crawl tieba"

    def long_desc(self):
        return "Crawl baidu tieba data to a MySQL database."

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("-a", dest="spargs", action="append", default=[], metavar="NAME=VALUE",
                          help="set spider argument (may be repeated)")
        parser.add_option("-o", "--output", metavar="FILE",
                          help="dump scraped items into FILE (use - for stdout)")
        parser.add_option("-t", "--output-format", metavar="FORMAT",
                          help="format to use for dumping items with -o")

        parser.add_option("-p", "--pages", nargs=2, type="int", dest="pages", default=[],
                          help="set the range of pages you want to crawl")
        parser.add_option("-g", "--good", action="store_true", dest="good_only", default=False,
                          help="only crawl good threads and their posts and comments")
        parser.add_option("-f", "--filter", type="str", dest="filter", default="",
                          help='set function name in "filter.py" to filter threads')
        parser.add_option("-s", "--see_lz", action="store_true", dest="see_lz", default=False,
                          help='enable "only see lz" mode')

    def set_pages(self, pages):
        if len(pages) == 0:
            begin_page = 1
            end_page = 999999
        else:
            begin_page = pages[0]
            end_page = pages[1]
        if begin_page <= 0:
            raise UsageError("The number of begin page must not be less than 1!")
        if begin_page > end_page:
            raise UsageError("The number of end page must not be less than that of begin page!")
        self.settings.set('BEGIN_PAGE', begin_page, priority='cmdline')
        self.settings.set('END_PAGE', end_page, priority='cmdline')

    def run(self, args, opts):
        self.set_pages(opts.pages)
        self.settings.set('GOOD_ONLY', opts.good_only)
        self.settings.set('SEE_LZ', opts.see_lz)
        if opts.filter:
            try:
                opts.filter = eval('filter.' + opts.filter)
            except:
                raise UsageError("Invalid filter function name!")
        self.settings.set("FILTER", opts.filter)
        cfg = config.config()
        if len(args) >= 3:
            raise UsageError("Too many arguments!")

        # 处理编码
        for i in range(len(args)):
            if isinstance(args[i], bytes):
                args[i] = args[i].decode("utf8")

        # 设置配置数据库的
        self.settings.set('MYSQL_HOST', cfg.config['MYSQL_HOST'])
        self.settings.set('MYSQL_USER', cfg.config['MYSQL_USER'])
        self.settings.set('MYSQL_PASSWD', cfg.config['MYSQL_PASSWD'])

        if len(args) == 1:
            # 单个参数多个tbname,但是部分库或者
            self.singleton_arg(args, cfg, opts)
        elif len(args) >= 2:
            # 多个参数处理tbname和dbname 分库去执行
            self.prototype_arg(args, cfg, opts)
        else:
            # 走配置文件
            print("走配置文件的逻辑.................")
            dbname = list(cfg.config['MYSQL_DBNAME'].values())[0]
            self.loadConfig(cfg, opts, dbname)

    # 单个参数的处理
    def singleton_arg(self, args, cfg, opts):
        # 获取数据库的名字,不拆库
        dbnameList = list(cfg.config['MYSQL_DBNAME'].values())

        dbnameDict=cfg.config['MYSQL_DBNAME']
        print("数据库名字dbName", dbnameList[0])
        # 获取传入的参数
        tbnames = args[0]
        # 切割传入的参数  支持多个贴吧名
        tbnameList = tbnames.split(',')
        print("tbnameList的长度:", len(tbnameList))
        if tbnameList is None or len(tbnameList) < 1:
            self.loadConfig(cfg=cfg, opts=opts, dbname=dbnameList[0])
        else:
            # 遍历参数的贴吧名
            for tbname in tbnameList:
                print("当前tbname:", tbname)
                print("贴吧名:", tbname, "数据库名:", dbnameList[0])
                self.loadNewConfigDbNameAndTbName(cfg, tbname, dbnameDict, dbnameList[0])
                self.process_config(tbname, dbnameList[0], cfg, opts)
            print("批量执行多个爬虫..........")
            self.crawler_process.start()

    # 多个参数的处理,如果参数大于2个按照传参的来处理数据库分库逻辑
    def prototype_arg(self, args, cfg, opts):
        # 获取对应的贴吧集合和数据库集合
        tbnameList = args[0].split(',')
        dbnameList = args[1].split(',')

        if len(tbnameList) != len(dbnameList):
            # 多参数读取配置文件
            dbname = list(cfg.config['MYSQL_DBNAME'].values())[0]
            self.loadConfig(cfg, opts, dbname)

        else:
            dbnameDict = cfg.config['MYSQL_DBNAME']
            print("dbname", dbnameDict)
            # 如果是输入的db喝tb直接用 分库逻辑
            for index in range(len(tbnameList)):
                tbname = tbnameList[index]
                dbname = dbnameList[index]
                # 执行配置
                print("贴吧名:", tbname, "数据库名:", dbname)
                # 拼接和处理新的数据库名字和贴吧名字
                self.loadNewConfigDbNameAndTbName(cfg,tbname,dbnameDict,dbname)
                self.process_config(tbname, dbname, cfg, opts)
            print("统一执行..........")
            self.crawler_process.start()

    # 组装新的参数进入config.json之后读取新的文件
    def loadNewConfigDbNameAndTbName(self,cfg,tbname,dbnames,dbname):
        tbnames = cfg.config['DEFAULT_TIEBA']
        if tbname not in tbnames:
            tbnames.append(tbname)
        #数据库配置的存放
        dbnames[tbname] = dbname
        # dbnames.setdefault(tbname, dbname)

    # 加载配置文件
    def loadConfig(self, cfg, opts, dbname):
        # 如果没有 读取项目默认配置文件的贴吧名
        # 存入数组贴吧名
        tbnames = cfg.config['DEFAULT_TIEBA']
        for tbname in tbnames:
            self.process_config(tbname, dbname, cfg, opts)
        print("统一执行..........")
        self.crawler_process.start()

    # 执行处理配置
    def process_config(self, tbname, dbname, cfg, opts):
        self.settings.set('TIEBA_NAME', tbname, priority='cmdline')
        self.settings.set('MYSQL_DBNAME', dbname, priority='cmdline')
        # 初始化数据库
        print("开始初始化数据库配置........")
        config.init_database(cfg.config['MYSQL_HOST'], cfg.config['MYSQL_USER'], cfg.config['MYSQL_PASSWD'],
                             dbname)
        print("初始化数据库配置完成........")
        log = config.log(tbname, dbname, self.settings['BEGIN_PAGE'], opts.good_only, opts.see_lz)
        self.settings.set('SIMPLE_LOG', log)
        #
        self.crawler_process.crawl('tieba', **opts.spargs)
        # self.crawler_process.join()

        # runner = CrawlerRunner()

        # @defer.inlineCallbacks
        # def crawl():
        #     yield runner.crawl(TiebaSpider,**opts.spargs)
        #     reactor.stop()
        #
        # crawl()
        # reactor.run()  # the script will block here until the last crawl call is finished
        cfg.save()
        print("保存cfg..........")