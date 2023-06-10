#!/usr/bin/env python
# encoding: utf-8
import time

from amazon_scrapy_spider.selenium_utils import create_wire_proxy_chrome, webdriver_get

if __name__ == '__main__':
    result = []
    for i in range(1):
        start = time.time()
        driver = create_wire_proxy_chrome(headless=True, image_mode=False)
        url = "https://www.amazon.com/Best-Sellers/zgbs/"

        url = "https://www.amazon.com/Best-Sellers-Amazon-Devices-Accessories/zgbs/amazon-devices/ref=zg_bs_nav_0"

        driver = webdriver_get(driver, url)
        # driver.get('https://dev.kdlapi.com/testproxy')
        # 获取页面内容
        # print(driver.page_source)
        # 延迟3秒后关闭当前窗口，如果是最后一个窗口则退出
        spend_time = time.time() - start
        print(spend_time)
        result.append(spend_time)
        print("响应结果大小为:", len(driver.page_source) / 1024 ** 2, "字节")

        with open("category_example1.html", "w") as file:
            file.write(driver.page_source)

        print()
    import numpy as np
    print(np.mean(result))
