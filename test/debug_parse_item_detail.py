from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from amazon_scrapy_spider.selenium_utils import webdriver_get

if __name__ == '__main__':
    # selenium 启动浏览器，然后解析网页

    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())  # 调试直接看这儿
    url = "https://www.amazon.com/Squishmallows-20-Inch-Wendy-Frog-Pet/dp/B0BMNFFV4C/ref=zg-bsnr_pet-supplies_sccl_2/147-7122655-1204148?pd_rd_w=8DG37&content-id=amzn1.sym.309d45c5-3eba-4f62-9bb2-0acdcf0662e7&pf_rd_p=309d45c5-3eba-4f62-9bb2-0acdcf0662e7&pf_rd_r=Y5GBQBVP1ZG149H2SFMG&pd_rd_wg=zN4Cx&pd_rd_r=6eb4203a-ee77-48d5-89b1-3d162d6f249f&pd_rd_i=B0BMNFFV4C&psc=1"
    driver = webdriver_get(driver, url)  # 如果多次都打开网页失败，那就是ip被封了，关掉代理用本地默认ip 刷新就可以
    element = driver.find_elements(By.XPATH, "xpath selector")  # 提取元素例子

    # 元素的对象还没取好，可参考 amazon_scrapy_spider/amazon_scrapy_spider/items.py
    # 最后再整理起来就可以了
