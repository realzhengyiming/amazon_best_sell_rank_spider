from dataclasses import asdict

import pandas as pd
import scrapy
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from amazon_scrapy_spider.cus_request import SeleniumRequest, RightTabRequest
from amazon_scrapy_spider.items import Item, Category, TreeLevel
from amazon_scrapy_spider.selenium_utils import get_base_url, webdriver_get
from amazon_scrapy_spider.selenium_utils import scrol_to_buttom, get_this_level_item_urls


class AmozonSpiderSpider(scrapy.Spider):
    """
    基于scrapySpider的爬虫模块

    通过安居客城市列表访问安居客网站中全国所有小区的页面 并通过Pipeline处理数据
    """

    name = "amozon"
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'amazon_scrapy_spider.middlewares.MyMiddleware': 400,  # 自定义的爬虫下载中间件
        },
        'DEFAULT_REQUEST_HEADERS': {
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.amazon.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/64.0.3282.186 Safari/537.36',
        },
        "LOG_LEVEL": "WARNING",

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
        category_url = RightTabRequest(self.url).parse(change_en_language=True)

        for category, url in category_url[:1]:  # 只测一个主题
            # yield SeleniumRequest(url=url, callback=self.parse_category1_items, meta={'url': url, "category": category})
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
        for text, url in this_page_items:
            item = Item()
            item['title'] = text

            item['url'] = url
            category = Category(name=response.meta.get("category"), tree_level=TreeLevel.FirstLevel)
            category = asdict(category)
            item['belongs_category'] = category
            item['first_level'] = category
            print("item", item)
            yield item

    # def parse(self, response):
    #
    #     """
    #     解析城市小区列表页面，并根据每个城市小区数量的不同执行不同的爬取策略
    #     1.如果城市小区数大于 3000 需划分行政区 划分后每个子行政区小区数也不能大于3000
    #     2.小区数少于3000 则开始遍历
    #     :param response:
    #     :return:
    #     """
    #
    #     selector = Selector(text=response.body)
    #     local = selector.xpath('//*[@id="list-content"]/div[1]/span/em[1]/text()').extract()[0]
    #     if int(selector.xpath('//*[@id="list-content"]/div[1]/span/em[2]/text()').extract()[
    #                0]) > settings['MAX_COMMUNITY_LIMIT']:
    #         self.log('当前地区:' + local + ',小区数超过阈值,需要划分行政区', level=log.DEBUG)
    #         for url in self.parse_area_divisions(selector):
    #             yield scrapy.Request(url=url, callback=self.parse_area, meta={'url': url})
    #     else:
    #         yield scrapy.Request(url=response.meta['url'], callback=self.parse_area, meta={'url': response.meta['url']},
    #                              dont_filter=True)

    # def parse_community(self, response):
    #     """
    #     从小区详细信息页面提取数据 pipeline会做后续的处理
    #     :param response:小区页面response
    #     :return:
    #     """
    #     selector = Selector(text=response.body)
    #     item = AnjukeItem()
    #     item['anjuke_id'] = re.sub("\D", "", response.meta['url'])
    #     data_list = selector.xpath('//*[@id="basic-infos-box"]/dl/dd/text()').extract()  # 包含了一系列数据
    #     item['property_type'] = data_list[0]
    #     item['property_price'] = data_list[1]
    #     item['total_area'] = data_list[2]
    #     item['total_family'] = data_list[3]
    #     item['built_year'] = data_list[4]
    #     item['total_parking'] = data_list[5]
    #     item['plot_ratio'] = data_list[6]
    #     item['green_ratio'] = data_list[7]
    #     item['built_company'] = data_list[8]
    #     item['property_company'] = data_list[9]
    #     item['name'] = \
    #         selector.xpath('/html/body/div[2]/div[3]/div[1]/h1/text()').extract()[0].replace('"', '').split()[0]
    #
    #     # 正则匹配 获得小区坐标
    #     pos_text = selector.xpath('/html/body/script[11]/text()').extract()
    #
    #     p_x = settings['ANJUKE_COMMUNITY_POS_LNG_RE']
    #     p_y = settings['ANJUKE_COMMUNITY_POS_LAT_RE']
    #     try:
    #         pos_x = re.search(p_x, str(pos_text)).group().replace('lng : "', '')
    #         pos_y = re.search(p_y, str(pos_text)).group().replace('lat : "', '')
    #         pos_bd09 = [pos_x, pos_y]
    #     except AttributeError:
    #         pos_bd09 = []
    #     item['pos_bd09'] = pos_bd09
    #
    #     # 正则匹配获得历史价格信息
    #     p_price = settings['ANJUKE_COMMUNITY_PRICE_RE']
    #
    #     try:
    #         price_dict = str(re.search(p_price, str(pos_text)).group().replace('data :', '').split())
    #         price_dict = eval(price_dict[:price_dict.find('ajaxUrl')].replace('\n', '')[2:-8])
    #         item['average_price_months'] = price_dict['community']
    #         item['average_price_now'] = price_dict['comm_midprice']
    #         item['comm_midchange'] = price_dict['comm_midchange']
    #     except AttributeError:
    #         self.r.lpush('REDIS_ANJUKE_LOST_INFO_URL', response.meta['url'])  # 收集重要信息缺失小区
    #         item['average_price_months'] = 0
    #         item['average_price_now'] = 0
    #         item['comm_midchange'] = 0
    #
    #     yield item
