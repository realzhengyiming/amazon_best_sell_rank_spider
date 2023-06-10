import os

import scrapy

from amazon_scrapy_spider.cus_request import RightTabRequest
from amazon_scrapy_spider.selenium_utils import get_base_url, get_right_category_urls
from config import PROJECT_ROOT


class amazonSpiderSpider(scrapy.Spider):
    """
    基于scrapySpider的爬虫模块

    通过安居客城市列表访问安居客网站中全国所有小区的页面 并通过Pipeline处理数据
    """

    name = "test_amazon"
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
        "LOG_LEVEL": "WARNING",
        # "LOG_LEVEL": "ERROR",

        # 禁用并发请求
        "CONCURRENT_REQUESTS": 2,  # 默认多少并发，忘记了，直接启动把
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,

        # 设置请求延迟时间为1秒
        "DOWNLOAD_DELAY": 0.5,

        # 设置下载超时时间为3秒
        "DOWNLOAD_TIMEOUT": 5,

        "FEED_FORMAT": 'csv',  # 设置存储格式为 CSV
        "FEED_EXPORT_HEADERS": False,  # 不输出表头
        "DEPTH_PRIORITY": 1  # 广度优先

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
        category_url = RightTabRequest(self.url, headless=False,
                                       image_mode=False).parse()
        print("len of category_url", len(category_url))
        output_path = os.path.join(PROJECT_ROOT, "output")
        os.makedirs(output_path, exist_ok=True)
        with open(os.path.join(output_path, "category1_url_table.csv"), "w") as file:
            for category, url in category_url:
                file.write(f"{category};{url}")

        for category, url in category_url[:1]:  # 只测一个主题
            print("category, url", category, url)
            yield scrapy.Request(url=url, callback=self.parse_category1_items, meta={'url': url, "category": category,
                                                                                     "level": 1})

    def parse_category1_items(self, response):  # 详情页一级（递归
        print("meta", response.meta)
        driver = response.meta.get("driver")
        if driver is None:
            print(driver)
        category_name = response.meta.get("category")
        level = response.meta.get("level")
        category_url = response.request.url
        print(f"现在是第{level}:{category_name}:{category_url}")
        # 末尾进行二级的获得与遍历
        # 提取一下二级的  # 然后提取一下三级的，依次递归了，然后我需要优先深度遍历，这样好一些？

        if level != 3:  # 第三级，最后一级了
            # 获得右侧 category_url
            category_url_list = get_right_category_urls(driver)  # 没有就不用下一级了
            # print("request url", response.request.url)
            print("level:", level, "子主题数量", len(category_url_list))
            for category, url in category_url_list:
                print("category, url", category, url)
                result = scrapy.Request(url=url, callback=self.parse_category1_items,
                                        meta={'url': url, "category": category,
                                              "level": level + 1}, dont_filter=True)  # 难道被过滤了？
                print(result)
                yield result

        print("")
        # driver.quit()  # 最后才关闭
