import os
import pickle
import time
from typing import List
from urllib.parse import urlparse

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from seleniumwire import webdriver as wire_webdriver  # pip install selenium-wire
from webdriver_manager.chrome import ChromeDriverManager
# 改成一个对象来封装也挺好的
from webdriver_manager.firefox import GeckoDriverManager

from config import PROXY_USER, PROXY_PASSWORD, PROXY_PORT, PROXY_HOST, HEADLESS_MODE, IMAGE_MODE, PROJECT_ROOT

# 创建Chrome浏览器对象

RETRY_TIME = 4


# @tenacity.retry(stop=tenacity.stop_after_attempt(5), wait=tenacity.wait_fixed(0.8))
def webdriver_get(driver, url, retry_time=5, wait_time=0.1):
    html_content = '<html><head><meta name="color-scheme" content="light dark"></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">Request was throttled. Please wait a moment and refresh the page</pre></body></html>'
    # 打开网页
    driver.implicitly_wait(1)  # 设置等待时间为10秒
    driver.get(url)
    for i in range(retry_time):
        if driver.page_source == html_content:
            driver.refresh()
        else:
            return driver
    print("重试多次后还是失败了！")  # 会有问题，一级分类已经搞定
    return driver


def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = parsed_url.scheme + '://' + parsed_url.netloc
    return base_url


# 这个是最耗时间的
def scroll_to_buttom(driver, wait_time=1):  # 滚动到底下刷新出来，展开最大的情况，全屏
    old_height = driver.execute_script('return document.body.scrollHeight')
    # 先滚动到最底部
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000);")

    for i in range(3):
        target_element = driver.find_element(By.XPATH, '//*[@class="a-pagination"]')
        driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", target_element)
        time.sleep(1)

    while True:  # 这个滚动的有bug ，不行 todo 数量不够
        # todo 页面不对也可能报错 try
        target_element = driver.find_element(By.XPATH, '//*[@class="a-pagination"]')
        driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", target_element)
        time.sleep(1)

        new_height = driver.execute_script('return document.body.scrollHeight')
        if old_height != new_height:
            old_height = new_height
        else:
            break
    print("结尾这", len(get_this_level_item_urls(driver)))
    return driver


def get_right_category_urls(driver) -> List[List]:  # category_name, url
    right_tab_list = driver.find_elements(By.XPATH, '//div[@role="group"]/div')
    category_url_list = []
    for i in right_tab_list:
        try:
            result = i.find_element(By.XPATH, 'a')
            url = result.get_attribute("href")
            category_url_list.append([i.text, url])
        except NoSuchElementException:
            print("url为空")
            category_url_list.append([i.text, None])
    return category_url_list


def get_this_level_item_urls(driver) -> List[List]:
    xpath = '//*[@id="gridItemRoot"]/div/div[2]/div/a[2]'  # 获取了图片部份的url
    a_list = driver.find_elements(By.XPATH, xpath)  # .//a[@class="a-link-normal"]/@href')
    item_urls = [[a.text, a.get_attribute("href")] for a in a_list]
    return item_urls


def create_wire_proxy_chrome(headless=HEADLESS_MODE, image_mode=IMAGE_MODE, page_load_strategy="eager"):
    options = {
        "headless": headless
    }
    options2 = wire_webdriver.ChromeOptions()
    options2.add_argument('--lang=en-US')
    options2.add_argument('--force-country-code=US')
    options2.add_experimental_option('excludeSwitches', ['enable-logging'])

    # if page_load_strategy:
    #     options2.page_load_strategy = page_load_strategy  # 渲染模式 normal, edger, none

    if headless:
        options2.add_argument('--headless')
    if not image_mode:
        prefs = {
            "profile.managed_default_content_settings.images": 2  # 不渲染图片，减少内存占用
        }
        options2.add_experimental_option("prefs", prefs)  # 设置无图模式

    if PROXY_USER and PROXY_PASSWORD and PROXY_PORT and PROXY_HOST:
        proxy_dict = {"proxy": {
            'http': f'http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}',
            'https': f'http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}',
        }}
        options.update(proxy_dict)

    driver = wire_webdriver.Chrome(seleniumwire_options=options, executable_path=ChromeDriverManager().install(),
                                   options=options2)
    driver.header_overrides = {'Accept-Language': 'en-US,en;q=0.9', "referer": "https://www.amazon.com"}  # 设置接收英语
    return driver


def create_wire_proxy_firefox(headless=HEADLESS_MODE):
    options = {
        "headless": headless
    }

    if PROXY_USER and PROXY_PASSWORD and PROXY_PORT and PROXY_HOST:
        proxy_dict = {"proxy": {
            'http': f'http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}',
            'https': f'http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}',
        }}
        options.update(proxy_dict)

    options2 = FirefoxOptions()
    options2.headless = True
    driver = wire_webdriver.Firefox(seleniumwire_options=options, executable_path=GeckoDriverManager().install(),
                                    options=options2)
    return driver


def pickle_cookie(driver):
    cookies = driver.get_cookies()
    store_path = os.path.join(PROJECT_ROOT, "cache")
    os.makedirs(store_path, exist_ok=True)
    path = os.path.join(store_path, "cookie.pkl")
    with open(path, 'wb') as f:
        pickle.dump(cookies, f)


def set_en_language_cookie(driver):
    driver.add_cookie({'domain': '.amazon.com', 'expiry': 1716907356, 'httpOnly': False, 'name': 'lc-main', 'path': '/',
                       'secure': False, 'value': 'en_US'})
    return driver


# def filter_url(url):
#     if hexists(url, category_keys):
#         return True
#     return False


if __name__ == '__main__':
    options = wire_webdriver.ChromeOptions()
    options.add_argument('--lang=en')
    options.add_argument('--headless')

    prefs = {
        "profile.managed_default_content_settings.images": 2  # 不渲染图片，减少内存占用
    }
    options.add_experimental_option("prefs", prefs)
    driver = wire_webdriver.Chrome(options=options, executable_path=ChromeDriverManager().install())

    url = "https://www.amazon.com/Best-Sellers/zgbs/"
    base_url = get_base_url(url)
    driver = webdriver_get(driver, url)
