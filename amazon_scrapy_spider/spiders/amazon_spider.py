import os
from typing import List
from urllib.parse import urljoin

import scrapy
from scrapy import Selector
from scrapy_redis.spiders import RedisSpider

from amazon_scrapy_spider.items import Item, Category, Level, RequestType
from amazon_scrapy_spider.selenium_utils import get_base_url
from config import PROJECT_ROOT


# todo 能跑了，下一步就是改成 scrapy-redis
# class amazonSpiderSpider(scrapy.Spider):
class amazonSpiderSpider(RedisSpider):
    """
    基于scrapySpider的爬虫模块

    通过安居客城市列表访问安居客网站中全国所有小区的页面 并通过Pipeline处理数据
    """

    name = "amazon"
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
        "CONCURRENT_REQUESTS": 2,  # 默认多少并发，忘记了，直接启动把
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,

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
            # 'example.pipelines.ExamplePipeline': 300,  # 这个改成我自己的，我需要item吗？需要的，如果要完整的断点续爬
            'scrapy_redis.pipelines.RedisPipeline': 400,  # 前面过滤了重复，后面的管道就也不要了
        },


        'REDIS_URL': "redis://127.0.0.1:6379",  # redis 地址
        # "JOBDIR": "amazon_cache",  # 互相干扰的意思咯
        # "keep_fragments": True,
        "DUPEFILTER_KEY": f"{name}:dupefilter",  # 这样才可以吗
        "REDIS_ENCODING": 'utf-8'

    }
    allowed_domains = ["www.amazon.com"]
    url = "https://www.amazon.com/Best-Sellers/zgbs/"
    base_url = get_base_url(url)
    # scrapy_redis 相关
    redis_key = f"{name}:start_urls"
    max_idle_time = 7


    def category_items(self, response) -> List[Item]:
        current_level = response.meta.get("level")
        xpath = '//*[@id="gridItemRoot"]/div/div[2]/div/a[2]'  # 获取了图片部份的url
        a_tags = Selector(response).xpath(xpath)
        item_urls = [[a.xpath(".//text()").get(), a.xpath("@href").extract_first()] for a in a_tags]

        # todo 改，能增加价格的就增加价格
        item_list = []
        for index, (text, url) in enumerate(item_urls):
            item = Item()
            item['title'] = text
            item['bsr'] = index + 1
            item['url'] = url
            item['belongs_category'] = response.meta.get("category")
            item['belongs_level'] = current_level
            item_list.append(item)
        return item_list

    def _right_sub_category_extract(self, response):
        right_tab_list = Selector(response).xpath('//div[@role="group"]/div')
        category_url_list = []
        for i in right_tab_list:
            sub_category_name = "".join(i.xpath(".//text()").getall())
            url = i.xpath('a/@href').get()

            if url is None:
                category_url_list.append([i.text, None])
            else:
                url = urljoin(self.base_url, url)
                category_url_list.append([sub_category_name, url])
        return category_url_list

    def subcategory_extract(self, response) -> List[scrapy.Request]:
        level = response.meta.get("level")
        old_category = response.meta.get("category")
        subcategory_list = []
        if level != Level.ThirdLevel.value:  # 第三级，最后一级了
            category_url_list = self._right_sub_category_extract(response)  # 没有就不用下一级了
            if len(category_url_list) != 0:
                print("level:", level, len(category_url_list))
                for category, url in category_url_list:  # 只测一个主题 todo 没有递归，此处，这是为什么。
                    print("category, url", category, url)
                    scrapy_request = scrapy.Request(url=url, callback=self.parse,
                                                    meta={'url': url, "category": f"{old_category}/" + category,
                                                          "level": level + 1,
                                                          "request_type": RequestType.CategoryRequest},
                                                    )
                    subcategory_list.append(scrapy_request)
        return subcategory_list

    def category_next_page(self, response) -> List[scrapy.Request]:
        next_list = []
        meta = response.meta
        # 下一页，next page 有这个直接就可以了
        next_page_url_xpath = '//div[@role="navigation"]/ul/li[@class="a-last"]/a/@href'
        suffix_page_url = Selector(response).xpath(next_page_url_xpath).extract_first()
        if suffix_page_url is not None:
            next_page_url = urljoin(self.base_url, suffix_page_url)
            meta['url'] = next_page_url
            scrapy_request = scrapy.Request(url=next_page_url, callback=self.parse, meta=meta,)
            next_list.append(scrapy_request)
        return next_list

    def parse(self, response):  # category 页面 提取item；翻页category
        level = response.meta.get("level")
        if level != Level.RootLevel.value:  # 种子，第一个bsr 页面，不提取item
            item_list = self.category_items(response)
            self.logger.info(f"item_list: level:{level}, item_list:{len(item_list)}")
            for item in item_list:
                yield item

        next_page_requests = self.category_next_page(response)
        self.logger.info(f"next_page: level:{level}, next_page_requests:{len(next_page_requests)}")
        for next_request in next_page_requests:
            yield next_request

        subcategory_list = self.subcategory_extract(response)  # 抓取下一级category
        for i in subcategory_list:
            print("subcategory_list", i)
        self.logger.info(f"subcategory_list: level:{level}, subcategory_list:{len(subcategory_list)}")
        for subcategory_request in subcategory_list:
            yield subcategory_request
