# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# useful for handling different item types with a single interface
import json

from scrapy.http import HtmlResponse

from amozon_scrapy_spider.redis_util import write_error_to_redis
from amozon_scrapy_spider.selenium_utils import webdriver_get, create_wire_proxy_chrome, change_en


class ChromeMiddleware(object):
    def process_request(self, request, spider):
        # 每个都创建一个才可以？
        # 在发送请求前对请求进行处理
        request.headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        if spider.name == 'amozon':  # 发起一个新的请求
            driver = create_wire_proxy_chrome()
            driver = webdriver_get(driver, request.url, wait_time=2)
            driver = change_en(driver)
            body = driver.page_source
            response = HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)
            response.meta.update({"driver": driver})  # driver 都带过去了，item结束后要把driver quit掉才可以
            return response

    def process_response(self, request, response, spider):
        # 在收到响应后对响应进行处理
        if response.status == 403:
            # 如果返回状态码为403，则重新发送该请求
            return request.replace(dont_filter=True)
        else:
            return response


class FirfoxMiddleware(object):
    def process_request(self, request, spider):
        # 每个都创建一个才可以？
        # 在发送请求前对请求进行处理
        request.headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        if spider.name == 'amozon':  # 发起一个新的请求

            driver = create_wire_proxy_chrome()  # 试试原来的
            driver = webdriver_get(driver, request.url, wait_time=2)

            body = driver.page_source
            response = HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)
            response.meta.update({"driver": driver})
            return response

    def process_response(self, request, response, spider):
        html_content = '<html><head><meta name="color-scheme" content="light dark"></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">Request was throttled. Please wait a moment and refresh the page</pre></body></html>'
        # 在收到响应后对响应进行处理
        if response.status == 403:
            # 如果返回状态码为403，则重新发送该请求
            return request.replace(dont_filter=True)
        elif response.body == html_content:
            # 把失败的写入数据库，或者写入redis中去
            write_error_to_redis(json.dumps({"url": response.request.url, "level": response.meta.get("level"),
                                             "category": response.request.meta.get("category")}))
            return response
        else:
            return response
