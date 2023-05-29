from amozon_scrapy_spider.selenium_utils import create_wire_proxy_firefox

driver = create_wire_proxy_firefox()

driver.get('https://dev.kdlapi.com/testproxy')

# 获取页面内容
print(driver.page_source)

# 延迟3秒后关闭当前窗口，如果是最后一个窗口则退出
driver.close()
