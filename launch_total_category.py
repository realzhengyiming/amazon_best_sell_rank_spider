import time

from scrapy import cmdline

# cmdline.execute('scrapy crawl amazon -o test.csv -t csv'.split())
# cmdline.execute('scrapy crawl amazon'.split())

start = time.time()
cmdline.execute('scrapy crawl amazon'.split())
print(time.time() - start)

