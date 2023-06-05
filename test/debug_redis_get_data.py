# redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
import redis

from amazon_scrapy_spider.redis_util import redis_pool

r = redis.Redis(connection_pool=redis_pool)
# 将错误信息推入 Redis 列表
data = r.lrange('amazon:items', 0, -1)
import json

with open("items_data.json", "w") as file:
    for i in [item.decode('utf-8') for item in data]:
        file.write(json.dumps(i) + "\n")
