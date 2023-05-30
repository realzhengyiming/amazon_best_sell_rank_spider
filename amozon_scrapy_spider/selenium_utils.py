import os
import pickle
import string
import time
import zipfile
from typing import List
from urllib.parse import urlparse

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from seleniumwire import webdriver as wire_webdriver  # pip install selenium-wire
from webdriver_manager.chrome import ChromeDriverManager
# 改成一个对象来封装也挺好的
from webdriver_manager.firefox import GeckoDriverManager

from amozon_scrapy_spider.redis_util import hexists
from config import PROXY_USER, PROXY_PASSWORD, PROXY_PORT, PROXY_HOST, HEADLESS_MODE, IMAGE_MODE, PROJECT_ROOT

# 创建Chrome浏览器对象

RETRY_TIME = 4


def webdriver_get(driver, url, retry_time=10, wait_time=5):
    html_content = '<html><head><meta name="color-scheme" content="light dark"></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">Request was throttled. Please wait a moment and refresh the page</pre></body></html>'
    # 打开网页
    # driver.implicitly_wait(wait_time)  # 设置等待时间为10秒
    driver.get(url)
    time.sleep(0.5)
    for i in range(retry_time):
        if driver.page_source == html_content:
            driver.refresh()
            time.sleep(0.1)
        else:
            return driver
    print("重试多次后还是失败了！")  # 会有问题，一级分类已经搞定
    return driver


def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = parsed_url.scheme + '://' + parsed_url.netloc
    return base_url


# 切换语言
def change_en(driver):
    driver = load_pickled_cookie(driver)
    # 直接修改cookie 就好了
    driver.refresh()

    # # 切换语言
    # change_language = driver.find_element(By.XPATH, '//*[@id="icp-nav-flyout"]')
    # change_language.click()
    #
    # selected_en = driver.find_element(By.XPATH, '//*[@id="icp-language-settings"]/div[2]/div/label/span/span')
    # selected_en.click()
    #
    # save_change = driver.find_element(By.XPATH, '//*[@id="icp-save-button"]/span/input')
    # save_change.click()
    return driver


# def scroll_to_buttom(driver, wait_time=1):
#     last_height = driver.execute_script('return document.body.scrollHeight')
#     while True:
#         # 执行JavaScript，对页面进行滚动
#         driver.execute_script('window.scrollTo(0, document.body.scrollHeight - 1000);')
#         # driver.execute_script("window.scrollBy(0, -550);")
#
#         # 等待页面加载完成
#         time.sleep(wait_time)  # 强心等了一秒（等待把东西加载出来）
#         # 判断是否还有可以滚动的内容
#         new_height = driver.execute_script('return document.body.scrollHeight')
#
#         if new_height == last_height:
#             break
#         else:
#             last_height = new_height
#     print("已经滚动完了所有内容")

def scroll_to_buttom(driver, wait_time=1):  # 滚动到底下刷新出来，展开最大的情况，全屏
    old_height = driver.execute_script('return document.body.scrollHeight')
    while True:
        target_element = driver.find_element(By.XPATH, '//*[@id="navBackToTop"]/div')
        # 创建 ActionChains 对象
        actions = ActionChains(driver)
        # 将鼠标移动到目标元素上
        actions.move_to_element(target_element)
        # 对目标元素进行微调
        actions.move_by_offset(0, -200)
        # 执行操作
        actions.pause(wait_time)
        actions.perform()
        new_height = driver.execute_script('return document.body.scrollHeight')
        if old_height != new_height:
            old_height = new_height
        else:
            break


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


def create_proxy_chrome():
    def create_proxyauth_extension(tunnelhost, tunnelport, proxy_username, proxy_password, scheme='http',
                                   plugin_path=None):
        """代理认证插件

        args:
            tunnelhost (str): 你的代理地址或者域名（str类型）
            tunnelport (int): 代理端口号（int类型）
            proxy_username (str):用户名（字符串）
            proxy_password (str): 密码 （字符串）
        kwargs:
            scheme (str): 代理方式 默认http
            plugin_path (str): 扩展的绝对路径

        return str -> plugin_path
        """

        if plugin_path is None:
            plugin_path = 'vimm_chrome_proxyauth_plugin.zip'

        manifest_json = """
	    {
	        "version": "1.0.0",
	        "manifest_version": 2,
	        "name": "Chrome Proxy",
	        "permissions": [
	            "proxy",
	            "tabs",
	            "unlimitedStorage",
	            "storage",
	            "<all_urls>",
	            "webRequest",
	            "webRequestBlocking"
	        ],
	        "background": {
	            "scripts": ["background.js"]
	        },
	        "minimum_chrome_version":"22.0.0"
	    }
	    """

        background_js = string.Template(
            """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                    singleProxy: {
                        scheme: "${scheme}",
                        host: "${host}",
                        port: parseInt(${port})
                    },
                    bypassList: ["foobar.com"]
                    }
                };

            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "${username}",
                        password: "${password}"
                    }
                };
            }

            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
            """
        ).substitute(
            host=tunnelhost,
            port=tunnelport,
            username=proxy_username,
            password=proxy_password,
            scheme=scheme,
        )
        with zipfile.ZipFile(plugin_path, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        return plugin_path

    proxyauth_plugin_path = create_proxyauth_extension(
        tunnelhost="r847.kdltps.com",  # 隧道域名
        tunnelport="15818",  # 端口号
        proxy_username="t18533708977798",  # 用户名
        proxy_password="ukoaa3t8"  # 密码
    )

    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_extension(proxyauth_plugin_path)

    # 每次都创建了一个新的
    options = webdriver.ChromeOptions()
    options.add_argument('--lang=en')
    options.add_argument('--headless')

    prefs = {
        "profile.managed_default_content_settings.images": 2  # 不渲染图片，减少内存占用
    }
    options.add_experimental_option("prefs", prefs)
    options.add_extension(proxyauth_plugin_path)

    # driver = webdriver.Chrome(options=options, executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
    return driver


def create_wire_proxy_chrome(headless=HEADLESS_MODE, image_mode=IMAGE_MODE):
    options = {
        "headless": headless
    }
    options2 = webdriver.ChromeOptions()
    if headless:
        options2.add_argument('--lang=en')
        options2.add_argument('--headless')
    if not image_mode:
        prefs = {
            "profile.managed_default_content_settings.images": 2  # 不渲染图片，减少内存占用
        }
        options2.add_experimental_option("prefs", prefs)  # 设置无图模式

    if PROXY_USER and PROXY_PASSWORD and PROXY_PORT and PROXY_HOST:
        proxy_dict = {
            'http': f'http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}',
            'https': f'http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}',
        }
        options.update(proxy_dict)

    driver = wire_webdriver.Chrome(seleniumwire_options=options, executable_path=ChromeDriverManager().install(),
                                   options=options2)
    return driver


def create_wire_proxy_firefox(headless=HEADLESS_MODE):
    options = {
        "headless": headless
    }

    if PROXY_USER and PROXY_PASSWORD and PROXY_PORT and PROXY_HOST:
        proxy_dict = {
            'http': f'http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}',
            'https': f'http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}',
        }
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


def load_pickled_cookie(driver):
    driver.add_cookie({'domain': '.amazon.com', 'expiry': 1716907356, 'httpOnly': False, 'name': 'lc-main', 'path': '/',
                       'secure': False, 'value': 'en_US'})

    # path = os.path.join(PROJECT_ROOT, "cache", "cookie.pkl")
    # with open(path, 'rb') as f:
    #     cookies = pickle.load(f)
    #     for cookie in cookies:
    #         driver.add_cookie(cookie)
    return driver


def filter_url(url):
    if hexists(url):
        return True
    return False


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.add_argument('--lang=en')
    options.add_argument('--headless')

    prefs = {
        "profile.managed_default_content_settings.images": 2  # 不渲染图片，减少内存占用
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options, executable_path=ChromeDriverManager().install())

    url = "https://www.amazon.com/Best-Sellers/zgbs/"
    base_url = get_base_url(url)
    driver = webdriver_get(driver, url)
    driver = change_en(driver)  # ，所以不返回任何东西都可以
