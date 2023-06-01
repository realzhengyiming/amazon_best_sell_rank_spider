import os
from dataclasses import asdict

import pandas as pd
import scrapy
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from amazon_scrapy_spider.cus_request import RightTabRequest
from amazon_scrapy_spider.items import Item, Category, TreeLevel
from amazon_scrapy_spider.redis_util import write_category_item_number_to_redis, hexists
from amazon_scrapy_spider.selenium_utils import get_base_url, webdriver_get, get_right_category_urls
from amazon_scrapy_spider.selenium_utils import scroll_to_buttom, get_this_level_item_urls
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
        "CONCURRENT_REQUESTS": 2,  # 默认多少并发，忘记了，直接启动把
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,

        # 设置请求延迟时间为1秒
        "DOWNLOAD_DELAY": 0.5,

        # 设置下载超时时间为3秒
        "DOWNLOAD_TIMEOUT": 5,

        "FEED_FORMAT": 'csv',  # 设置存储格式为 CSV
        "FEED_EXPORT_HEADERS": False,  # 不输出表头
        "DEPTH_PRIORITY": 1,  # 广度优先

        "CSV_OUTPUT_DIR": os.path.join(PROJECT_ROOT, "output"),
        "ITEM_PIPELINES": {
            'amazon_scrapy_spider.pipelines.CsvFilePipeline': 300,
        }

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
                                       image_mode=IMAGE_MODE).parse()
        print("len of category_url", len(category_url))
        with open(os.path.join(PROJECT_ROOT, "output", "category1_url_table.csv"), "w") as file:
            for category, url in category_url:
                file.write(f"{category};{url}")

        for category, url in category_url:  # 只测一个主题
            print("category, url", category, url)
            if not hexists(url, CRAWLED_CATEGORY_KEYS):  # 未提取过item的 category 页面才执行
                yield scrapy.Request(url=url, callback=self.parse_category1_items,
                                     meta={'url': url, "category": category,
                                           "level": 1}, dont_filter=True)

    def parse_category1_items(self, response):  # 详情页一级（递归

        driver = response.meta.get("driver")
        category_name = response.meta.get("category")
        level = response.meta.get("level")
        category_url = response.request.url

        this_page_items = []
        try:
            next_page_elm = driver.find_element(By.XPATH, '//div[@role="navigation"]/ul/li[@class="a-last"]')
            # next_page_elm = driver.find_element(By.XPATH, '//div[@role="navigation"]/ul/li[@class="a-last"]')
            next_page_class_attr = next_page_elm.get_attribute("class")
        except NoSuchElementException:
            next_page_class_attr = ""
            next_page_elm = None

        scroll_to_buttom(driver, 2)
        this_page_items += get_this_level_item_urls(driver)

        # print(len(this_page_items))
        # print(next_page_class_attr)

        # 翻页模块
        while next_page_class_attr == "a-last" and next_page_elm is not None:
            next_page_url = next_page_elm.find_element(By.XPATH, 'a').get_attribute("href")
            # print("有下一页", next_page_url)
            driver = webdriver_get(driver, next_page_url)
            scroll_to_buttom(driver, 2)
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
        print("total num", len(this_page_items), response.request.url)  # todo 滑动的数量也不够，应该是前100才对
        write_category_item_number_to_redis(category_url,
                                            f"{category_name}:{len(this_page_items)}")
        # 作为记录，已经够了的就不写入了，后面再进行一轮去重和增量提取

        if level != 3:  # 第三级，最后一级了
            # 获得右侧 category_url
            category_url_list = get_right_category_urls(driver)  # 没有就不用下一级了
            driver.quit()  # 最后才关闭
        else:
            category_url_list = []
            driver.quit() #

        for index, (text, url) in enumerate(this_page_items):
            item = Item()
            item['title'] = text
            item['bsr'] = index + 1
            item['url'] = url
            category = Category(name=response.meta.get("category"), tree_level=TreeLevel.FirstLevel)
            category = asdict(category)
            item['belongs_category'] = category
            item['first_level'] = category
            # print("item", item)
            yield item

        # 末尾进行二级的获得与遍历
        # 提取一下二级的  # 然后提取一下三级的，依次递归了，然后我需要优先深度遍历，这样好一些？

        if level != 3:  # 第三级，最后一级了
            if len(category_url_list) != 0 :
                print("level:", level, len(category_url_list))
                for category, url in category_url_list:  # 只测一个主题 todo 没有递归，此处，这是为什么。
                    if not hexists(url, CRAWLED_CATEGORY_KEYS):  # 未提取过item的 category 页面才执行
                        print("category, url", category, url)
                        yield scrapy.Request(url=url, callback=self.parse_category1_items,
                                             meta={'url': url, "category": category,
                                                   "level": level + 1}, dont_filter=True)


