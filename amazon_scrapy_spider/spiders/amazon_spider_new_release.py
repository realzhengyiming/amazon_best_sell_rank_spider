import os
from typing import List
from urllib.parse import urljoin

import scrapy
from scrapy import Selector
from scrapy_redis.spiders import RedisSpider

from amazon_scrapy_spider.items import Item, Level, RequestType
from amazon_scrapy_spider.selenium_utils import get_base_url
from amazon_scrapy_spider.spiders.amazon_spider import AmazonCategorySpider
from config import PROJECT_ROOT


class AmazonCategoryNewReleaseSpider(AmazonCategorySpider):  # 直接继承category spider
    """
    基于scrapySpider的爬虫模块
    """

    name = "amazon_new_relase"
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
        "CONCURRENT_REQUESTS": 2,  # todo 按照实际的情况可以修改此处
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,  # todo 按照实际的情况可以修改此处

        # 设置请求延迟时间为1秒
        "DOWNLOAD_DELAY": 1,

        # 设置下载超时时间为3秒
        "DOWNLOAD_TIMEOUT": 5,

        "FEED_EXPORT_HEADERS": False,  # 不输出表头
        "DEPTH_PRIORITY": 1,  # 广度优先

        "CSV_OUTPUT_DIR": os.path.join(PROJECT_ROOT, "output"),
        # "ITEM_PIPELINES": {
        #     'amazon_scrapy_spider.pipelines.CsvFilePipeline': 300,
        # }

        # scrapy-redis相关的
        'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
        'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
        'SCHEDULER_PERSIST': True,

        'ITEM_PIPELINES': {
            # 'scrapy_redis.pipelines.RedisPipeline': 400,  # 前面过滤了重复，后面的管道就也不要了
            'amazon_scrapy_spider.pipelines.NewReleaseRedisPipeline': 400,  # 使用了自定义的 new release 的item pipeline
        },

        'REDIS_URL': "redis://127.0.0.1:6379",  # redis 地址
        # "keep_fragments": True,
        "DUPEFILTER_KEY": f"{name}:dupefilter",  # 检查重复的
        "REDIS_ENCODING": 'utf-8',

    }
    allowed_domains = ["www.amazon.com"]
    url = "https://www.amazon.com/Best-Sellers/zgbs/"

    # todo 两个类型的种子，作为判断用，加入到redis中的种子必须和这儿的保持一致.这两个应该不需要改
    root_url_list = ["https://www.amazon.com/Best-Sellers/zgbs/",
                     "https://www.amazon.com/gp/new-releases/ref=zg_bs_tab"]

    base_url = get_base_url(url)
    # scrapy_redis 相关
    redis_key = f"{name}:start_urls"
    max_idle_time = 7

    # 直接继承category spider，所以不需要再实现解析，直接复用
