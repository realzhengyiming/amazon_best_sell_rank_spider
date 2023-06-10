import csv
import os
from urllib.parse import urljoin

from scrapy_redis.pipelines import RedisPipeline

from amazon_scrapy_spider.items import Item
from amazon_scrapy_spider.redis_util import write_item_to_redis, hexists
from amazon_scrapy_spider.spiders.amazon_item_detail_spider import AmazonItemSpider
from amazon_scrapy_spider.spiders.amazon_spider import AmazonCategorySpider
from config import CRAWLED_ITEM_KEYS


class CsvFilePipeline:
    """写成.csv文件，no header"""

    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.tmp_file = None
        self.csv_writer = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(output_dir=crawler.settings.get('CSV_OUTPUT_DIR'))

    def open_spider(self, spider):
        # current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")、
        current_time = "2023-05-31_22:00"
        csv_file_dir = os.path.join(self.output_dir, spider.name)
        os.makedirs(csv_file_dir, exist_ok=True)
        csv_name = os.path.join(self.output_dir, csv_file_dir, current_time + ".csv")
        self.tmp_file = open(csv_name, 'a+')
        self.csv_writer = csv.writer(self.tmp_file, dialect='excel')
        # 写入首行

    def close_spider(self, spider):
        self.tmp_file.close()

    def process_item(self, item, spider):
        if isinstance(item, Item):
            url = item.get("url")
            bsr = item.get("bsr")
            belongs_category = item.get("belongs_category")
            item_name = item.get("title")
            unique_code = f"{url}|{belongs_category.get('tree_level')}|{bsr}"

            if not hexists(unique_code, CRAWLED_ITEM_KEYS):  # 写入过的不再写入
                self.csv_writer.writerows([[str(s) for s in item.values()]])
                write_item_to_redis(unique_code, item_name)

            return item


class CustomRedisPipeline(RedisPipeline):

    def _process_item(self, item, spider):
        key = self.item_key(item, spider)
        data = self.serialize(item)
        self.server.rpush(key, data)
        # 增加写入一个新的列表中作为 详情页爬虫的种子提取处

        if "url" in item and item.get("url"):
            spider_name = AmazonItemSpider.name
            item_redis_key = f"{spider_name}:start_urls"
            full_url = urljoin(spider.base_url, item.get("url"))
            self.server.rpush(item_redis_key, full_url)
        return item