# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# useful for handling different item types with a single interface
import os
import time

import tenacity
from scrapy.http import HtmlResponse
from selenium.common import NoSuchElementException
from urllib3.exceptions import MaxRetryError

from amazon_scrapy_spider.items import RequestType
from amazon_scrapy_spider.selenium_utils import webdriver_get, create_wire_proxy_chrome, create_wire_proxy_firefox, \
    scroll_to_buttom
from config import PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASSWORD, PROJECT_ROOT


# 这两个都是下载中间件


class WebMiddleware(object):
    _proxy = (PROXY_HOST, PROXY_PORT)  # 快代理的隧道代理的host 和 port

    # 处理 process_request 请求后返回回来的内容，决定是生成新的 response 还是重试
    def process_response(self, request, response, spider):
        html_content = '<html><head><meta name="color-scheme" content="light dark"></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">Request was throttled. Please wait a moment and refresh the page</pre></body></html>'
        # 在收到响应后对响应进行处理
        print(f"response.status:{response.status}")
        if response.body == html_content:
            # 把失败的写入数据库，或者写入redis中去
            spider.logger.info("重新加入队列，下次重试")
            return request.replace(dont_filter=True, meta=request.meta)
        elif response.status == 403:
            # 如果返回状态码为403，则重新发送该请求
            "Type the characters you see in this image:"
            spider.logger.info("重新加入队列，下次重试")
            return request.replace(dont_filter=True, meta=request.meta)
        elif response.status == 429:
            spider.logger.info("重新加入队列，下次重试")
            return request.replace(dont_filter=True, meta=request.meta)
        else:
            spider.logger.info("success")
            # 正常的status，直接返回正常的response即可
            return response


@tenacity.retry(stop=tenacity.stop_after_attempt(3), wait=tenacity.wait_fixed(0.5))
def selenium_and_scroll(url, need_scroll=True):
    driver = create_wire_proxy_chrome()
    driver = webdriver_get(driver, url, wait_time=0.1)

    try:
        if need_scroll:
            driver = scroll_to_buttom(driver)
    except NoSuchElementException:
        print("没有找到元素，url", url)
        driver.quit()  # 找不到就关闭， 为的是不造成资源占用
    return driver  # 关闭后为空，返回也会报错，就可以抓到


class ChromeMiddleware(WebMiddleware):
    def process_request(self, request, spider):
        # 默认使用这个打开详情页
        useagent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        request.headers['user-agent'] = useagent
        request.headers['accept-language'] = "en-GB,en;q=0.9"
        request.headers["Connection"] = "close"  # 避免使用隧道道理的时候换ip失败

        need_scroll = True

        if request.url == spider.url:
            # https://www.amazon.com/Best-Sellers/zgbs/
            request.meta.update({'url': request.url, "category": "root",
                                 "request_type": RequestType.Root,
                                 "level": 0})  # 如果是root节点的话，记录一下不提取item就可以了
            need_scroll = False

        request_type = request.meta.get("request_type")
        print("request_type:", request_type, "need_scroll", need_scroll, "timestamp", time.time(), request.url)
        if request_type is RequestType.CategoryRequest or request_type is RequestType.Root:
            try:
                driver = selenium_and_scroll(request.url, need_scroll)
                if not driver:
                    raise Exception("driver 为空")
                body = driver.page_source
                response = HtmlResponse(request.url, body=body, encoding='utf-8', request=request)
                driver.quit()
                return response  # 不再经过默认的其他 request 下载中间件，直接给调度器
            except MaxRetryError as e:
                spider.logger.debug("打印中间件错误, 重新提交请求")
                spider.logger.debug(e)
                return request.replace(dont_filter=True, meta=request.meta)
            except tenacity.RetryError as e:
                spider.logger.debug("打印中间件错误, 重新提交请求")
                spider.logger.debug(e)
                return request.replace(dont_filter=True, meta=request.meta)
            except Exception as e:
                spider.logger.debug("打印中间件错误, 重新提交请求")
                spider.logger.debug(e)
                return request.replace(dont_filter=True, meta=request.meta)
        elif request_type is RequestType.ItemRequest:
            # 如何代理不为空就，配置代理就可以了
            if PROXY_PASSWORD and PROXY_USER and PROXY_HOST and PROXY_PORT:
                request.meta['proxy'] = "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": PROXY_USER,
                                                                                "pwd": PROXY_PASSWORD,
                                                                                "proxy": ':'.join(self._proxy)}

            return None  # 继续执行请求
            # detail item 类型使用代理就可以了，什么也不做，就是使用默认的了
        else:
            print("第三种情况，检查内容")  # 更新了这部份检查
            print("request_type:", request_type, "timestamp", time.time(), request.url)
            print(request.meta)

class FirfoxMiddleware(object):
    def process_request(self, request, spider):
        # 每个都创建一个才可以？
        # 在发送请求前对请求进行处理
        request.headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'

        driver = create_wire_proxy_firefox()  # 试试原来的
        driver = webdriver_get(driver, request.url, wait_time=0.1)

        body = driver.page_source
        response = HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)
        response.meta.update({"driver": driver})
        return response
