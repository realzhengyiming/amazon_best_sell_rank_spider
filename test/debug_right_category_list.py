#!/usr/bin/env python
# encoding: utf-8
import time

from amazon_scrapy_spider.selenium_utils import create_wire_proxy_chrome, webdriver_get, get_right_category_urls

if __name__ == '__main__':
    start = time.time()
    driver = create_wire_proxy_chrome(headless=False, image_mode=True)
    driver = webdriver_get(driver,
                           'https://www.amazon.com/Best-Sellers-Amazon-Devices-Accessories-Amazon-Device-Accessories/zgbs/amazon-devices/370783011/ref=zg_bs_nav_amazon-devices_1')
    category_url_list = get_right_category_urls(driver)
    print(len(category_url_list))

    # 获取页面内容
    print(driver.page_source)

    # 延迟3秒后关闭当前窗口，如果是最后一个窗口则退出
    print(time.time() - start)
    # time.sleep(3)
    # driver.close()

    print()
