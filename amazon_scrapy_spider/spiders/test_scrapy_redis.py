import os

import scrapy
from scrapy_redis.spiders import RedisSpider

from amazon_scrapy_spider.items import Item, Category, Level
from amazon_scrapy_spider.selenium_utils import get_base_url
from config import PROJECT_ROOT


class test_item(scrapy.Item):
    url = scrapy.Field()
    rank = scrapy.Field()


# todo 能跑了，下一步就是改成 scrapy-redis
# class amazonSpiderSpider(scrapy.Spider):
class amazonSpiderSpider(RedisSpider):
    """
    基于scrapySpider的爬虫模块

    通过安居客城市列表访问安居客网站中全国所有小区的页面 并通过Pipeline处理数据
    """

    name = "test_redis"
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'amazon_scrapy_spider.middlewares.ChromeMiddleware': 400,  # 自定义的爬虫下载中间件
        },
        'DEFAULT_REQUEST_HEADERS': {
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.amazon.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/64.0.3282.186 Safari/537.36',
        },
        # "LOG_LEVEL": "WARNING",
        "LOG_LEVEL": "INFO",

        # 禁用并发请求
        "CONCURRENT_REQUESTS": 100,  # 默认多少并发，忘记了，直接启动把
        "CONCURRENT_REQUESTS_PER_DOMAIN": 100,

        # 设置请求延迟时间为1秒
        # "DOWNLOAD_DELAY": 0.5,
        "DOWNLOAD_DELAY": 0,

        # 设置下载超时时间为3秒
        "DOWNLOAD_TIMEOUT": 5,

        # "DEPTH_PRIORITY": 1,  # 广度优先

        "CSV_OUTPUT_DIR": os.path.join(PROJECT_ROOT, "output"),
        # "ITEM_PIPELINES": {
        #     'amazon_scrapy_spider.pipelines.CsvFilePipeline': 300,
        # }

        # 下面开始都是redis的
        'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
        'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
        'SCHEDULER_PERSIST': True,

        'ITEM_PIPELINES': {
            # 'example.pipelines.ExamplePipeline': 300,  # 这个改成我自己的，我需要item吗？需要的，如果要完整的断点续爬
            'scrapy_redis.pipelines.RedisPipeline': 400,  # 前面过滤了重复，后面的管道就也不要了
        },
        'REDIS_URL': "redis://127.0.0.1:6379",
        # "JOBDIR": "amazon_cache",  # 互相干扰的意思咯
        # "keep_fragments": True,
        "DUPEFILTER_KEY": "test_redis:dupefilter",  # 这样才可以吗
        "REDIS_ENCODING": 'utf-8'

    }
    # allowed_domains = ["*"]
    url = "https://127.0.0.1:8080"
    base_url = get_base_url(url)
    redis_key = "test_redis:start_urls"
    max_idle_time = 7

    # 再增加一级呗，简单改写 def parse_seperate 就好了
    def parse(self, response):
        print(1)
        print(response)
        print()
        import time
        print("正在暂停")
        time.sleep(2)

        # todo redis的item不过滤的，这是为什么
        for i in range(3):
            item = test_item()
            item['url'] = response.request.url
            item['rank'] = i
            yield item

        for i in range(100000000):  # 100000000
            yield scrapy.Request(url=f"http://127.0.0.1:8080/target/helloworld/{i}", callback=self.parse_second,
                                 )  # 当成完成了yield出去后  # yield后到哪里去了
        print("跑完了")

    def parse_second(self, response):
        print("近来第二级")
        url = response.request.url
        number = url.split("/")[-1]
        item = Item()
        item['title'] = f'item{number}'+ "sdfasdfdasfasdfdsafjad;fjdsa;lkfjasdl;fkjsdafl;adsjflkasdjfkasdjf;asdfjasdlk;fjasd;lfajsdf;adsjf;ajf;aklsdfjas;lfjasl;kfjasdflkjasdflkasjdf;ladsjf;ad"  # title: str
        item['url'] = url + "asdfjadfjads;fjadsf;ajdsfk;adsjf;askdjfa;lkfjalk;fajsfkldajsfasfhiuerwtiyukgfhasudtghwetrdf"
        item['belongs_category'] = str(Category(item['title'], level=Level.ThirdLevel))  # belongs_category: Category  # 所在类别

        item['bsr'] = str(number) + ":second"
        yield item
        print("完成第二级")
