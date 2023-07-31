import os

from scrapy import Selector
from scrapy_redis.spiders import RedisSpider

from amazon_scrapy_spider.items import DetailItem
from amazon_scrapy_spider.selenium_utils import get_base_url
from config import PROJECT_ROOT


class AmazonItemSpider(RedisSpider):
    """
    基于scrapySpider的爬虫模块

    通过安居客城市列表访问安居客网站中全国所有小区的页面 并通过Pipeline处理数据
    """

    name = "amazon_item_detail"  # 不要修改此爬虫名字，CustomRedisPipeline 中会读取此爬虫的名字
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'amazon_scrapy_spider.middlewares.ItemDetailMiddleware': 300,  # 增加request 类型的中间件
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
        "CONCURRENT_REQUESTS": 2,  # todo 按照实际的情况可以修改此处
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,  # todo 按照实际的情况可以修改此处

        # 设置请求延迟时间为1秒
        "DOWNLOAD_DELAY": 1,

        # 设置下载超时时间为3秒
        "DOWNLOAD_TIMEOUT": 5,

        "FEED_EXPORT_HEADERS": False,  # 不输出表头
        "DEPTH_PRIORITY": 1,  # 广度优先

        "CSV_OUTPUT_DIR": os.path.join(PROJECT_ROOT, "output"),

        # scrapy-redis相关的
        'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
        'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
        'SCHEDULER_PERSIST': True,

        'ITEM_PIPELINES': {
            'scrapy_redis.pipelines.RedisPipeline': 400,  # 详情页使用默认的就可以
            # 如果希望保存到其他地方，还可以写一个自己的管道，放在这个管道后面，优先级大于400这样。默认都直接写进redis，方便分布式
        },

        'REDIS_URL': "redis://127.0.0.1:6379",  # redis 地址
        # "keep_fragments": True,
        "DUPEFILTER_KEY": f"{name}:dupefilter",  # 检查重复的
        "REDIS_ENCODING": 'utf-8',
        "COOKIES_ENABLED": True
    }

    allowed_domains = ["www.amazon.com"]
    url = "https://www.amazon.com/Best-Sellers/zgbs/"
    base_url = get_base_url(url)
    # scrapy_redis 相关
    redis_key = f"{name}:start_urls"
    max_idle_time = 7  # 7s内如果redis中没有取到url就停止爬虫
    root_url_list = ["https://www.amazon.com/Best-Sellers/zgbs/",
                     "https://www.amazon.com/gp/new-releases/ref=zg_bs_tab"]

    def parse(self, response):  # category 页面 提取item；翻页category
        # todo 此处 写详情页的解析就可以，可以参考 test_scrapy_spider/test/debug_parse_item_detail.py 的解析
        item = DetailItem()
        # item['asin'] = response.request.url.split("dp/")[-1].split("/")[0]
        item['url'] = response.request.url
        # ....
        # xpath = '//*[@id="glow-ingress-block"]'
        # result = Selector(response).xpath(xpath).get()
        # result = result[0].xpath(".//text()").get()
        print("检查结果")
        # print(result)
        with open("test_item_html.html", "w") as file:
            file.write(response.text)

        yield item  # 就可以了
