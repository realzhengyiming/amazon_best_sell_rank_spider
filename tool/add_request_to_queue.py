"""
此代码用于将丢失的品类节点添加进爬虫待爬取的列表中。或用于只提取某个品类下的所有子品类的top100商品（因为类别的节点是树展开的形式）
手动修改main函数中的 品类目录地址，然后启动即可加入redis中，下次启动爬虫项目的时候就会读取到这个队列信息，并且开始爬取。
"""
import redis
from scrapy import Request, Spider
from scrapy_redis import picklecompat

from amazon_scrapy_spider.items import RequestType
from amazon_scrapy_spider.redis_util import redis_pool
from amazon_scrapy_spider.spiders.amazon_item_detail_spider import AmazonItemSpider
from amazon_scrapy_spider.spiders.amazon_item_detail_spider_new_release import AmazonNewReleaseItemSpider
from amazon_scrapy_spider.spiders.amazon_spider import AmazonCategorySpider
from amazon_scrapy_spider.spiders.amazon_spider_new_release import AmazonCategoryNewReleaseSpider

SPIDER_TYPE_MAPPING = {
    "AmazonCategorySpider": AmazonCategorySpider(),
    "AmazonCategoryNewReleaseSpider": AmazonCategoryNewReleaseSpider(),
    "AmazonItemSpider": AmazonItemSpider(),
    "AmazonNewReleaseItemSpider": AmazonNewReleaseItemSpider()
}


def _encode_request(spider_class, request):
    """Encode a request object"""
    obj = request.to_dict(spider=spider_class)
    return picklecompat.dumps(obj)


def add_category_request_to_redis_queue(spider_class, request):
    r = redis.Redis(connection_pool=redis_pool)
    encoding_request = _encode_request(spider_class, request)
    score = request.priority  # 0 就是最高优先级
    r.execute_command('ZADD', f"{spider_class.name}:requests", score, encoding_request)
    print("重新加入队列")


def package_request(url, meta, spider_class: Spider):
    """
    url: just url
    meta: meta format,example: meta = {'url': url, "category": f"root/Amazon Devices & Accessories/Amazon Device Accessories",
                "level": 3,
                "request_type": RequestType.CategoryRequest / RequestType.ItemRequest}
    spider_class: use SPIDER_TYPE_MAPPING value
    """
    scrapy_request = Request(url=url, callback=spider_class.parse, meta=meta, dont_filter=True)
    return scrapy_request


if __name__ == '__main__':
    # example 这个只能逐个添加，因为不同的request不同，多个就只能多个添加; 不启动爬虫，实际只是添加了一个request队列进入redis，下次
    # 启动爬虫就可以从redis中读取队列信息，开始爬取这个

    url = "https://www.amazon.com/Best-Sellers-Baby/zgbs/baby-products/ref=zg_bs_nav_0"
    spider_instance = SPIDER_TYPE_MAPPING.get("AmazonCategorySpider")
    request = package_request(url=url,
                              meta={'url': url,
                                    "category": f"root/Baby",
                                    "level": 1,
                                    "request_type": RequestType.CategoryRequest},
                              spider_class=spider_instance,
                              )
    print(request.priority)
    add_category_request_to_redis_queue(spider_instance, request)

    # 同时，把对应爬虫的 redis中的 dupefilter 删除，如果确定这一级往后都是没爬过的话  redis 中
    # 爬虫名：dupefilter ，例如 amazon:dupefilter
