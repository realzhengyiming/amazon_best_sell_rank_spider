# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# useful for handling different item types with a single interface
import json

import tenacity
from scrapy.http import HtmlResponse
from selenium.common import NoSuchElementException

from amazon_scrapy_spider.items import RequestType
from amazon_scrapy_spider.redis_util import write_error_to_redis
from amazon_scrapy_spider.selenium_utils import webdriver_get, create_wire_proxy_chrome, create_wire_proxy_firefox, \
    scroll_to_buttom


class WebMiddleware(object):

    # 处理 process_request 请求后返回回来的内容，决定是生成新的 response 还是重试
    def process_response(self, request, response, spider):
        html_content = '<html><head><meta name="color-scheme" content="light dark"></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">Request was throttled. Please wait a moment and refresh the page</pre></body></html>'
        # 在收到响应后对响应进行处理
        print("response.status", response.status)
        if response.body == html_content:
            # 把失败的写入数据库，或者写入redis中去
            write_error_to_redis(json.dumps({"url": response.request.url, "level": response.meta.get("level"),
                                             "category": response.request.meta.get("category")}))
            # 在收到响应后对响应进行处理
            print(response.status)
            return request.replace(dont_filter=True)  # 重新发起请求
        elif response.status == 403:
            # 如果返回状态码为403，则重新发送该请求
            "Type the characters you see in this image:"
            print(response.status)
            return request.replace(dont_filter=True)
        elif response.status == 429:
            print(response.text)
            print("代理是不是没钱了")
            # write_error_to_redis(json.dumps({"url": request.url, "level": response.meta.get("level"),
            #                                  "category": response.request.meta.get("category")}))
            return request.replace(dont_filter=True)  # 这种情况确实是重试,重新发一个请求给 调度器
        else:
            # 正常的status，直接返回正常的response即可
            return response


@tenacity.retry(stop=tenacity.stop_after_attempt(3), wait=tenacity.wait_fixed(0.5))
def selenium_and_scroll(url):
    driver = create_wire_proxy_chrome()
    driver = webdriver_get(driver, url, wait_time=0.1)
    try:
        driver = scroll_to_buttom(driver)
    except NoSuchElementException:
        print("没有找到元素，url", url)
        driver.quit()  # 找不到就关闭， 为的是不造成资源占用
    return driver  # 关闭后为空，返回也会报错，就可以抓到


class ChromeMiddleware(WebMiddleware):
    def process_request(self, request, spider):
        # 每个都创建一个才可以？
        # 在发送请求前对请求进行处理
        request.headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        if request.url == spider.url:
            # https://www.amazon.com/Best-Sellers/zgbs/
            request.meta.update({'url': request.url, "category": "root",
                                 "request_type": RequestType.Root,
                                 "level": 0})  # 如果是root节点的话，记录一下不提取item就可以了

        if request.meta.get("request_type") is RequestType.CategoryRequest:
            try:
                driver = selenium_and_scroll(request.url)
                try:
                    body = driver.page_source
                except Exception as e:
                    print(e)
                driver.quit()
                response = HtmlResponse(request.url, body=body, encoding='utf-8', request=request)
                return response
            except tenacity.RetryError as e:
                print("打印中间件错误")
                print(e)
                return request  # 重新发送请求到调度器
        elif request.meta.get("request_type") is RequestType.ItemRequest:
            pass  # todo 后面支持的类型 item 类型使用代理就可以了


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
