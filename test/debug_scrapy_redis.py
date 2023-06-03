import time

from scrapy import cmdline

# cmdline.execute('scrapy crawl amozon -o test.csv -t csv'.split())
# cmdline.execute('scrapy crawl amozon'.split())

start = time.time()
cmdline.execute('scrapy crawl test_redis'.split())
print(time.time() - start)

# todo 英语的状态，如何永远设置这个呢
# todo 全局的无图模式怎么没起效果
