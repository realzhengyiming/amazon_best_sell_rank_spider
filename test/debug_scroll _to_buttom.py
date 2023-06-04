#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import time

sys.path.extend(['/Users/zhengyiming/PycharmProjects/test_scrapy_spider'])
print(os.environ.get("PYTHONPATH"))

# from amazon_scrapy_spider.selenium_utils import create_wire_proxy_chrome, webdriver_get, scroll_to_buttom
from amazon_scrapy_spider.selenium_utils import create_wire_proxy_chrome, webdriver_get, scroll_to_buttom, \
    get_this_level_item_urls

if __name__ == '__main__':
    for i in [None, "eager", "normal"]:
        s1 = time.time()
        start = time.time()
        print("mode: ", i)
        # driver = create_wire_proxy_chrome(headless=False, image_mode=False, page_load_strategy=None)
        driver = create_wire_proxy_chrome(headless=False, image_mode=False, page_load_strategy=i)
        url = "https://www.amazon.com/best-sellers-books-Amazon/zgbs/books/ref=zg_bs_nav_0"
        driver = webdriver_get(driver, url=url)
        print(time.time() - start)

        # # scroll 到底部
        print("开始滚动...")
        s2 = time.time()
        driver = scroll_to_buttom(driver)  # 更新一下
        print(f"scroll time", time.time() - s2)
        print("滚动结束。。。")
        print("检查item数量")
        b = len(get_this_level_item_urls(driver))
        print("item数量", b)
        print()
        driver.quit()
        print(f"total spend{time.time()}")

        print("--------------")
        # print(selenium_and_scroll(url))
