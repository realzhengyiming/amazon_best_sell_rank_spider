# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# useful for handling different item types with a single interface
from scrapy.http import HtmlResponse

from amozon_scrapy_spider.selenium_utils import webdriver_get, create_proxy_chrome, create_wire_proxy_chrome, change_en


class ChromeMiddleware(object):
    def process_request(self, request, spider):
        # 每个都创建一个才可以？
        # 在发送请求前对请求进行处理
        request.headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        print("调用了自己的这个请求")

        if spider.name == 'amozon':  # 发起一个新的请求
            driver = create_wire_proxy_chrome()
            driver = webdriver_get(driver, request.url, wait_time=2)
            # if request.url.find("amozon.com") != -1:
                # 都要刷新一次...很麻烦，但是必须分离还要同时切换语言
            driver = change_en(driver)

            body = driver.page_source
            response = HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)
            response.meta.update({"driver": driver})
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
        print("调用了自己的这个请求")

        if spider.name == 'amozon':  # 发起一个新的请求

            driver = create_wire_proxy_chrome()  # 试试原来的
            driver = webdriver_get(driver, request.url, wait_time=2)

            body = driver.page_source
            response = HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)
            response.meta.update({"driver": driver})
            return response

    def process_response(self, request, response, spider):
        # 在收到响应后对响应进行处理
        if response.status == 403:
            # 如果返回状态码为403，则重新发送该请求
            return request.replace(dont_filter=True)
        else:
            return response
