import time

from scrapy import cmdline

# cmdline.execute('scrapy crawl amazon -o test.csv -t csv'.split())
# cmdline.execute('scrapy crawl amazon'.split())

start = time.time()
cmdline.execute('scrapy crawl amazon'.split())
print(time.time() - start)

# todo 英语的状态，如何永远设置这个呢
# todo 全局的无图模式怎么没起效果
