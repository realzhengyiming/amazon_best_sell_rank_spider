from typing import List

import scrapy
from scrapy.http import HtmlResponse
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from amozon_scrapy_spider.selenium_utils import webdriver_get, scrol_to_buttom, change_en, \
    get_right_category_urls, create_proxy_chrome


# 单纯打开重启的时候可以用这个
class SeleniumRequest(scrapy.Request):
    def __init__(self, url, callback, *args, **kwargs):
        options = webdriver.ChromeOptions()
        options.add_argument('--lang=en')
        options.add_argument('--headless')

        prefs = {
            "profile.managed_default_content_settings.images": 2  # 不渲染图片，减少内存占用
        }
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(options=options, executable_path=ChromeDriverManager().install())

        self.driver = driver
        super().__init__(url=url, callback=callback, *args, **kwargs)

    def __del__(self):
        self.driver.quit()

    def parse(self, response: HtmlResponse, slide_bottom=False, change_en_language=False):  # 默认不管
        self.driver = webdriver_get(self.driver, response.url)
        self.meta.update({"driver": self.driver})  # 这样好像会线程/进程不安全的
        if slide_bottom:
            scrol_to_buttom(self.driver)

        if change_en_language:
            change_en(self.driver)

        # 获取页面内容
        body = self.driver.page_source
        response = HtmlResponse(
            url=response.url,
            body=body,
            encoding='utf-8',
            request=self
        )

        response.meta.update({"driver": self.driver})  # 这样好像会线程/进程不安全的
        return response


class RightTabRequest:
    def __init__(self, url):
        self.url = url
        driver = create_proxy_chrome()
        self.driver = driver

    def parse(self, slide_bottom=False, change_en_language=False) -> List[List]:
        # category_name, url:  # 默认不管
        self.driver = webdriver_get(self.driver, self.url)
        if slide_bottom:
            scrol_to_buttom(self.driver)

        if change_en_language:
            change_en(self.driver)

        # 获取页面内容
        category_url_list = get_right_category_urls(self.driver)
        return category_url_list
