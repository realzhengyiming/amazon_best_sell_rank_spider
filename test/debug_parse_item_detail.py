from scrapy import Selector
from scrapy.http import HtmlResponse

from amazon_scrapy_spider.selenium_utils import webdriver_get, create_wire_proxy_chrome

if __name__ == '__main__':
    # selenium 启动浏览器，然后解析网页
    driver = create_wire_proxy_chrome(headless=False, image_mode=True)
    url = "https://www.amazon.com/Squishmallows-20-Inch-Wendy-Frog-Pet/dp/B0BMNFFV4C/ref=zg-bsnr_pet-supplies_sccl_2/147-7122655-1204148?pd_rd_w=8DG37&content-id=amzn1.sym.309d45c5-3eba-4f62-9bb2-0acdcf0662e7&pf_rd_p=309d45c5-3eba-4f62-9bb2-0acdcf0662e7&pf_rd_r=Y5GBQBVP1ZG149H2SFMG&pd_rd_wg=zN4Cx&pd_rd_r=6eb4203a-ee77-48d5-89b1-3d162d6f249f&pd_rd_i=B0BMNFFV4C&psc=1"

    url = "https://www.amazon.com/Introducing-alexa-voice-remote-pro/dp/B09RX4HKTD/ref=zg_bs_370783011_sccl_5/147-7122655-1204148?th=1"
    # url = "https://www.amazon.com/Best-Sellers-Audible-Books-Originals/zgbs/audible/ref=zg_bs_nav_0"
    driver = webdriver_get(driver, url)  # 如果多次都打开网页失败，那就是ip被封了，关掉代理用本地默认ip 刷新就可以

    response = HtmlResponse("", body=driver.page_source, encoding='utf-8', request="")

    # asin
    asin = url.split("dp/")[-1].split("/")[0]

    # 标题
    item_title = "".join(Selector(response).xpath('//*[@id="title"]').xpath(".//text()").extract()).strip()

    # 库存
    stock_status_xpath = '//*[@id="exports_desktop_outOfStock_buybox_message_feature_div"]/div'  # 库存状态
    result = Selector(response).xpath(stock_status_xpath)
    stock_status = "".join(result[0].xpath(".//text()").extract())

    # 首页
    item_host_url = Selector(response).xpath('//*[@id="bylineInfo_feature_div"]/div').xpath(".//a/@href").get()
    # item_host_name =

    custom_review_elm = Selector(response).xpath('//*[@id="reviewsMedley"]/div/div[1]/span[1]/span')

    rating_num = "".join(Selector(response).xpath('//*[@id="reviewsMedley"]/div/div[1]/span[1]/span/div[3]/span').xpath(".//text()").get()).split(" ")[-3]

    five_star_rate = "".join(Selector(response).xpath('//*[@id="histogramTable"]/tbody/tr[1]/td[3]/span[2]').xpath(".//text()").extract()).strip()
    four_star_rate = "".join(Selector(response).xpath('//*[@id="histogramTable"]/tbody/tr[2]/td[3]/span[2]/a').xpath(".//text()").extract()).strip()
    three_star_rate = "".join(Selector(response).xpath('//*[@id="histogramTable"]/tbody/tr[3]/td[3]/span[2]/a').xpath(".//text()").extract()).strip()
    two_star_rate = "".join(Selector(response).xpath('//*[@id="histogramTable"]/tbody/tr[4]/td[3]/span[2]/a').xpath(".//text()").extract()).strip()
    one_star_rate = "".join(Selector(response).xpath('//*[@id="histogramTable"]/tbody/tr[5]/td[3]/span[2]/a').xpath(".//text()").extract()).strip()

    item_price = ""
    # ASIN
    # 标题、
    # 商品rating数、
    # rating星级、
    # ratin星级分布、
    # 商品当前价格、
    # 折扣比例、
    # 价格状态、
    # 规格变体数量（一包几个＋颜色数量）、  不同商品好像不太一样
    # 站点、
    # 分类、
    # 分类节点、
    # BSR排名、
    # 上架时间、
    # 库存状态、
    # 五点描述

    #
    # rat

    # 详情页的解析，写出来
    # pass
    print(1)
    print(2)
