import os
from dataclasses import asdict
from urllib.parse import urljoin

import scrapy
from scrapy import Selector

from amazon_scrapy_spider.cus_request import RightTabRequest
from amazon_scrapy_spider.items import Item, Category, Level, RequestType
from amazon_scrapy_spider.redis_util import hexists
from amazon_scrapy_spider.selenium_utils import get_base_url
from config import HEADLESS_MODE, IMAGE_MODE, PROJECT_ROOT, CRAWLED_CATEGORY_KEYS


class amazonSpiderSpider(scrapy.Spider):
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
        "LOG_LEVEL": "ERROR",

        # 禁用并发请求
        "CONCURRENT_REQUESTS": 1,  # 默认多少并发，忘记了，直接启动把
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,

        # 设置请求延迟时间为1秒
        "DOWNLOAD_DELAY": 0.5,

        # 设置下载超时时间为3秒
        "DOWNLOAD_TIMEOUT": 5,

        "FEED_FORMAT": 'csv',  # 设置存储格式为 CSV
        "FEED_EXPORT_HEADERS": False,  # 不输出表头
        "DEPTH_PRIORITY": 1,  # 广度优先

        "CSV_OUTPUT_DIR": os.path.join(PROJECT_ROOT, "output"),
        # "ITEM_PIPELINES": {
        #     'amazon_scrapy_spider.pipelines.CsvFilePipeline': 300,
        # }

    }
    allowed_domains = ["*"]
    url = "https://www.amazon.com/Best-Sellers/zgbs/"
    base_url = get_base_url(url)

    def start_requests(self):
        """
        执行前置任务,完成爬虫初始化队列的生成,代理ip的获取，并启动爬虫。
        :return:
        """
        # 直接这一级就开始
        category_url = RightTabRequest(self.url, headless=HEADLESS_MODE,
                                       image_mode=IMAGE_MODE).parse()
        print("len of category_url", len(category_url))
        with open(os.path.join(PROJECT_ROOT, "output", "category1_url_table.csv"), "w") as file:
            for category, url in category_url:
                file.write(f"{category};{url}")

        for category, url in category_url:  # 只测一个主题 todo 后面改成 scrapy-redis
            print("category, url", category, url)
            if not hexists(url, CRAWLED_CATEGORY_KEYS):  # 未提取过item的 category 页面才执行
                yield scrapy.Request(url=url, callback=self.parse_category_content,
                                     meta={'url': url, "category": category,
                                           "request_type": RequestType.CategoryRequest,
                                           "level": 1}, dont_filter=True)

    def category_items(self, response):
        xpath = '//*[@id="gridItemRoot"]/div/div[2]/div/a[2]'  # 获取了图片部份的url
        a_tags = Selector(response).xpath(xpath)
        item_urls = [[a.xpath(".//text()").get(), a.xpath("@href").extract_first()] for a in a_tags]
        for index, (text, url) in enumerate(item_urls):
            item = Item()
            item['title'] = text
            item['bsr'] = index + 1
            item['url'] = url
            category = Category(name=response.meta.get("category"), level=Level.FirstLevel)
            category = asdict(category)
            item['belongs_category'] = category
            item['first_level'] = category
            yield item

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

    def subcategory_extract(self, response):
        level = response.meta.get("level")
        if level != 3:  # 第三级，最后一级了
            category_url_list = self._right_sub_category_extract(response)  # 没有就不用下一级了
            if len(category_url_list) != 0:
                print("level:", level, len(category_url_list))
                for category, url in category_url_list:  # 只测一个主题 todo 没有递归，此处，这是为什么。
                    print("category, url", category, url)
                    yield scrapy.Request(url=url, callback=self.parse_category_content,
                                         meta={'url': url, "category": category,
                                               "level": level + 1, "request_type": RequestType.CategoryRequest},
                                         dont_filter=True)

    def category_next_page(self, response):
        meta = response.meat
        # 下一页，next page 有这个直接就可以了
        next_page_url_xpath = '//div[@role="navigation"]/ul/li[@class="a-last"]/a/@href'
        suffix_page_url = Selector(response).xpath(next_page_url_xpath).extract_first()
        if suffix_page_url is not None:
            next_page_url = urljoin(self.base_url, suffix_page_url)
            meta['url'] = next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse_category_content, meta=meta, dont_filter=True)

    def parse_category_content(self, response):  # category 页面 提取item；翻页category
        level = response.meta.get("level")
        if level != 0:  # 种子，第一个bsr 页面，不提取item
            self.category_items(response)

        self.category_next_page(response)

        self.subcategory_extract(response)  # 抓取下一级category

