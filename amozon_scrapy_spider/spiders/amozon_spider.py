from dataclasses import asdict

import pandas as pd
import scrapy
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from amozon_scrapy_spider.cus_request import RightTabRequest
from amozon_scrapy_spider.items import Item, Category, TreeLevel
from amozon_scrapy_spider.selenium_utils import get_base_url, webdriver_get, change_en
from amozon_scrapy_spider.selenium_utils import scrol_to_buttom, get_this_level_item_urls
from config import HEADLESS_MODE, IMAGE_MODE


class AmozonSpiderSpider(scrapy.Spider):
    """
    基于scrapySpider的爬虫模块

    通过安居客城市列表访问安居客网站中全国所有小区的页面 并通过Pipeline处理数据
    """

    name = "amozon"
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'amozon_scrapy_spider.middlewares.ChromeMiddleware': 400,  # 自定义的爬虫下载中间件
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
        "CONCURRENT_REQUESTS": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,

        # 设置请求延迟时间为1秒
        "DOWNLOAD_DELAY": 1,

        # 设置下载超时时间为3秒
        "DOWNLOAD_TIMEOUT": 3,

    }
    allowed_domains = ["*"]
    url = "https://www.amazon.com/Best-Sellers/zgbs/"
    base_url = get_base_url(url)

    def write_into_csv(self, item):
        df = pd.DataFrame(item.dict())
        df.to_csv("test.csv", "")

    def start_requests(self):
        """
        执行前置任务,完成爬虫初始化队列的生成,代理ip的获取，并启动爬虫。
        :return:
        """
        # 直接这一级就开始
        category_url = RightTabRequest(self.url, headless=HEADLESS_MODE,
                                       image_mode=IMAGE_MODE).parse(
            change_en_language=True)
        print("len of category_url", len(category_url))
        for category, url in category_url:  # 只测一个主题
            yield scrapy.Request(url=url, callback=self.parse_category1_items, meta={'url': url, "category": category})

    # # todo 统一使用一样的中间件，后面再看看
    # def parse_right_level1_url(self, response):
    #     category_url_list = get_right_category_urls(self.driver)
    # def parse(self, response):
    #     print(response.meta)

    # def parse_category1_items(self, driver, meta):  # 详情页一级
    def parse_category1_items(self, response):  # 详情页一级
        driver = response.meta.get("driver")
        print("搞笑？")
        print("meta", response.meta)
        print("meta2", response.request.meta)
        this_page_items = []
        try:
            next_page_elm = driver.find_element(By.XPATH, '//div[@role="navigation"]/ul/li[@class="a-last"]')
            # next_page_elm = driver.find_element(By.XPATH, '//div[@role="navigation"]/ul/li[@class="a-last"]')
            next_page_class_attr = next_page_elm.get_attribute("class")
        except NoSuchElementException:
            next_page_class_attr = ""
            next_page_elm = None

        scrol_to_buttom(driver, 1)
        this_page_items += get_this_level_item_urls(driver)

        # print(len(this_page_items))
        # print(next_page_class_attr)

        # 翻页模块
        while next_page_class_attr == "a-last" and next_page_elm is not None:
            next_page_url = next_page_elm.find_element(By.XPATH, 'a').get_attribute("href")
            # print("有下一页", next_page_url)
            driver = webdriver_get(driver, next_page_url)
            change_en(driver)
            scrol_to_buttom(driver, 1)
            try:
                next_page_elm = driver.find_element(By.XPATH, '//div[@role="navigation"]/ul/li[@class="a-last"]')
                next_page_class_attr = next_page_elm.get_attribute("class")
                # 更新下一页的标签
                # print(next_page_elm.get_attribute("class"))
                this_page_items += get_this_level_item_urls(driver)

            except NoSuchElementException:
                this_page_items += get_this_level_item_urls(driver)
                # print("没找到")
                next_page_class_attr = ""

        # 直接把结果写入到csv中
        print("total num", len(this_page_items))  # todo 滑动的数量也不够，应该是前100才对
        for index, (text, url) in enumerate(this_page_items):
            item = Item()
            item['title'] = text
            item['bsr'] = index + 1
            item['url'] = url
            category = Category(name=response.meta.get("category"), tree_level=TreeLevel.FirstLevel)
            category = asdict(category)
            item['belongs_category'] = category
            item['first_level'] = category
            print("item", item)
            yield item
