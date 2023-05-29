#!/usr/bin/env python
# encoding: utf-8
import time

from amozon_scrapy_spider.selenium_utils import create_wire_proxy_firefox

if __name__ == '__main__':
    start = time.time()
    driver = create_wire_proxy_firefox()
    driver.get('https://dev.kdlapi.com/testproxy')

    # 获取页面内容
    print(driver.page_source)

    # 延迟3秒后关闭当前窗口，如果是最后一个窗口则退出
    print(time.time() - start)

    time.sleep(3)
    driver.close()
