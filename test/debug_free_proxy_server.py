import time as time

from amazon_scrapy_spider.selenium_utils import webdriver_get, scroll_to_buttom, create_wire_proxy_chrome

if __name__ == '__main__':
    # 测试下ip地址
    for i in range(1):
        start = time.time()

        # driver = create_wire_proxy_chrome(headless=False, image_mode=False, page_load_strategy="eager")
        driver = create_wire_proxy_chrome(headless=False, image_mode=False, page_load_strategy=None)
        # 直接折半，牛逼，卧槽，快很多，试试t

        url = "https://www.amazon.com/Best-Sellers/zgbs/"
        url = "https://www.amazon.com/Best-Sellers-Amazon-Devices-Accessories/zgbs/amazon-devices/ref=zg_bs_nav_0"
        driver = webdriver_get(driver, url)
        driver = scroll_to_buttom(driver)
        spend_time = time.time() - start
        print("spending time", spend_time)
        # time.sleep(60)
