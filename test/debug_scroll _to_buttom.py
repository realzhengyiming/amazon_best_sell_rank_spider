#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import time
sys.path.extend(['/Users/zhengyiming/PycharmProjects/test_scrapy_spider'])
print(os.environ.get("PYTHONPATH"))

from amazon_scrapy_spider.middlewares import selenium_and_scroll


# from amazon_scrapy_spider.selenium_utils import create_wire_proxy_chrome, webdriver_get, scroll_to_buttom
from amazon_scrapy_spider.selenium_utils import create_wire_proxy_chrome, webdriver_get, scroll_to_buttom, \
    get_right_category_urls, get_this_level_item_urls

if __name__ == '__main__':
    start = time.time()
    driver = create_wire_proxy_chrome(headless=False, image_mode=False)
    # url = "https://www.amazon.com/best-sellers-video-games/zgbs/videogames/ref=zg_bs_pg_2?_encoding=UTF8&pg=2"
    url = 'https://www.amazon.com/Best-Sellers-Beauty-Personal-Care/zgbs/beauty/ref=zg_bs_nav_0'
    url = "https://www.amazon.com/best-sellers-books-Amazon/zgbs/books/ref=zg_bs_nav_0"
    driver = webdriver_get(driver, url=url)
    # # driver.get('https://dev.kdlapi.com/testproxy')

    # # scroll 到底部
    print("开始滚动...")
    driver = scroll_to_buttom(driver)  # 更新一下
    print("滚动结束。。。")
    # # 获取页面内容
    # print(driver.page_source)
    # # 延迟3秒后关闭当前窗口，如果是最后一个窗口则退出
    print(time.time() - start)
    # # time.sleep(3)
    # driver.close()
    # result = get_right_category_urls(driver)
    print("检查item数量")
    b = len(get_this_level_item_urls(driver))
    print("item数量", b)
    print()
    driver.quit()
    # print(selenium_and_scroll(url))