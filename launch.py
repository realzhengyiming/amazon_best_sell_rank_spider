from scrapy import cmdline

# cmdline.execute('scrapy crawl amozon -o test.csv -t csv'.split())
# cmdline.execute('scrapy crawl amozon'.split())
cmdline.execute('scrapy crawl amozon -o test.csv -t csv'.split())
