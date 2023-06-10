#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import time

from scrapy import Selector
from scrapy.http import HtmlResponse

from amazon_scrapy_spider.items import Item

sys.path.extend(['/Users/zhengyiming/PycharmProjects/test_scrapy_spider'])
print(os.environ.get("PYTHONPATH"))

# from amazon_scrapy_spider.selenium_utils import create_wire_proxy_chrome, webdriver_get, scroll_to_buttom
from amazon_scrapy_spider.selenium_utils import create_wire_proxy_chrome, webdriver_get, scroll_to_buttom, \
    get_this_level_item_urls

if __name__ == '__main__':
    # for i in [None, "eager", "normal"]:
    for j in range(1):
        i = None
        s1 = time.time()
        start = time.time()
        print("mode: ", i)
        # driver = create_wire_proxy_chrome(headless=False, image_mode=False, page_load_strategy=None)
        driver = create_wire_proxy_chrome(headless=False, image_mode=False, page_load_strategy=i)
        url = "https://www.amazon.com/best-sellers-books-Amazon/zgbs/books/ref=zg_bs_nav_0"
        url = "https://www.amazon.com/best-sellers-books-Amazon/zgbs/books/ref=zg_bs_pg_2?_encoding=UTF8&pg=2"
        driver = webdriver_get(driver, url=url)
        driver = scroll_to_buttom(driver)  # 更新一下

        response = HtmlResponse("", body=driver.page_source, encoding='utf-8', request="")

        ## 下面开始写解析的测试部分
        # asin
        asin = url.split("dp/")[-1].split("/")[0]

        # 标题 例子
        item_title = "".join(Selector(response).xpath('//*[@id="title"]').xpath(".//text()").extract()).strip()

        xpath = '//*[@id="gridItemRoot"]/div'
        a_tags = Selector(response).xpath(xpath)

        # xpath = '//*[@id="gridItemRoot"]/div/div[2]/div'
        item_list = []
        for index, a in enumerate(a_tags):
            # items = [[a.xpath('@id').get(), a.xpath("./a[2]//text()").get(), a.xpath("./a[2]/@href").extract_first(), a.xpath("./div//text()").get(), a.xpath("./div[2]//text()").get(), a.xpath('.//img/@src').get()] for a in a_tags]
            # for index, (asin, text, url, rating_or_price1, rating_or_price2, img_url) in enumerate(items):
            item = Item()

            item["bsr"] = a.xpath('./div[1]/div//text()').get()
            other_info = a.xpath('./div[2]/div')

            item['asin'] = other_info.xpath('@id').get()
            item['title'] = other_info.xpath("./a[2]//text()").get()
            # item['bsr'] = index + 1
            item['url'] = other_info.xpath("./a[2]/@href").extract_first()
            item['belongs_category'] = response.meta.get("category")
            item['belongs_level'] = "current_level"

            num_div = len(other_info.xpath("./div"))
            rate = None
            price = None
            for i in range(num_div):
                data = other_info.xpath("./div[{}]//text()".format(i + 1)).get()
                if data is None:
                    continue
                if "out of" in data:
                    rate = data
                elif "$" in data:
                    price = data
                elif "from" in data:
                    new_data = other_info.xpath("./div[{}]/a/span/span//text()".format(i + 1)).get()
                    if "$" in new_data:
                        price = new_data

            # NOTE(chun): 这里确实会有price是None的
            if price is not None and "$" not in price:
                import pdb;

                pdb.set_trace()
            item['rating'] = rate
            item['price'] = price
            item['img_url'] = other_info.xpath('.//img/@src').get()
            item['from_url'] = response.url
            item_list.append(item)


        ##
        driver.quit()
        print(f"total spend{time.time()}")

        # print(selenium_and_scroll(url))
        print(time.time() - start)
        print("--------------")
        print()
