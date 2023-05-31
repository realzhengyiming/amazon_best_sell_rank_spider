#!/usr/bin/env python
# encoding: utf-8
import time

from amazon_scrapy_spider.selenium_utils import create_wire_proxy_chrome, webdriver_get, scroll_to_buttom

if __name__ == '__main__':
    start = time.time()
    driver = create_wire_proxy_chrome(headless=False, image_mode=False)
    url = "https://www.amazon.com/best-sellers-video-games/zgbs/videogames/ref=zg_bs_pg_2?_encoding=UTF8&pg=2"
    driver = webdriver_get(driver, url=url)
    # driver.get('https://dev.kdlapi.com/testproxy')

    # scroll 到底部
    scroll_to_buttom(driver)
    # 获取页面内容
    print(driver.page_source)
    # 延迟3秒后关闭当前窗口，如果是最后一个窗口则退出
    print(time.time() - start)
    # time.sleep(3)
    driver.close()
    print()
