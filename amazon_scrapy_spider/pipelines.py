import csv
import os

from amazon_scrapy_spider.items import Item
from amazon_scrapy_spider.redis_util import write_item_to_redis, hexists
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
