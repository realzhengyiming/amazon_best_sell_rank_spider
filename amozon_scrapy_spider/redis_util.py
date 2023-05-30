import json
from typing import Dict

import redis

from config import ERROR_KEYS, CRAWLED_CATEGORY_KEYS, ITEM_URLS

# 创建 Redis 连接池

redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)


def write_error_to_redis(error_info: str, error_keys=ERROR_KEYS):
    # 获取 Redis 连接对象
    r = redis.Redis(connection_pool=redis_pool)
    # 将错误信息推入 Redis 列表
    r.lpush(error_keys, error_info)


def write_category_item_number_to_redis(category, item_number, category_keys=CRAWLED_CATEGORY_KEYS):
    # 获取 Redis 连接对象
    r = redis.Redis(connection_pool=redis_pool)
    # 将错误信息推入 Redis 列表
    r.hset(category_keys, category, item_number)  # 不够的要补1李爱
    print("log ", category_keys, category, item_number)


def write_item_to_redis(item_url, item_name, table_name=ITEM_URLS):
    # 获取 Redis 连接对象
    r = redis.Redis(connection_pool=redis_pool)
    # 将错误信息推入 Redis 列表
    r.hset(table_name, item_url, item_name)  # 不够的要补1李爱
    print("log ", table_name, item_url, item_name)


def get_redis_hash(category_keys=CRAWLED_CATEGORY_KEYS) -> Dict:
    r = redis.Redis(connection_pool=redis_pool)
    result = r.hgetall(category_keys)
    return result


def hexists(field_key, category_keys=CRAWLED_CATEGORY_KEYS):
    r = redis.Redis(connection_pool=redis_pool)
    if r.hexists(category_keys, field_key):
        return True
    else:
        return False


if __name__ == '__main__':
    write_error_to_redis("hello world")
    write_category_item_number_to_redis("test", 100)
    category_dict = get_redis_hash()
    category_dict_keys = set([k.decode('utf-8') for k in category_dict])  # 改成写入url把
    print(category_dict_keys)

    print(hexists("test"))

    write_error_to_redis(json.dumps({"url": "test", "level": 1,
                                     "category": "device"}))
