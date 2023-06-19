from scrapy import Selector
from scrapy.http import HtmlResponse

from amazon_scrapy_spider.selenium_utils import create_wire_proxy_chrome, webdriver_get


def _right_sub_category_extract(response):
    right_tab_list = Selector(response).xpath('//div[@role="group"]/div')
    last_sub_category = not all([i.xpath(".//a").get() for i in right_tab_list])  # 如果不是全都有链接，那就是最底层的类别了，这时候不需要再找侧边
    if last_sub_category:
        print("最底层的类别了，不需要再提取右边类别")
        return []
    category_url_list = []
    for i in right_tab_list:
        sub_category_name = "".join(i.xpath(".//text()").getall())
        url = i.xpath('a/@href').get()
        if url is None:
            category_url_list.append([i.text, None])
        else:
            category_url_list.append([sub_category_name, url])
    return category_url_list


if __name__ == '__main__':
    url = "https://www.amazon.com/Best-Sellers-Pet-Supplies-Dog-ID-Tags/zgbs/pet-supplies/2975342011/ref=zg_bs_nav_pet-supplies_4_6602294011"  # 最底层类别
    url = "https://www.amazon.com/Best-Sellers-Pet-Supplies-Dog-ID-Tags-Collar-Accessories/zgbs/pet-supplies/6602294011/ref=zg_bs_unv_pet-supplies_4_2975317011_2"  # 非最底层类别
    url = "https://www.amazon.com/Best-Sellers-Digital-Music/zgbs/dmusic/ref=zg_bs_nav_0"  # 类root页面
    driver = create_wire_proxy_chrome(headless=False, image_mode=False)
    driver = webdriver_get(driver, url)

    response = HtmlResponse("", body=driver.page_source, encoding='utf-8', request="")

    # result = Selector(response).xpath('//*[@id="title"]').xpath(".//text()").extract()

    result = _right_sub_category_extract(response)
    print(len(result))
    print("result1")
