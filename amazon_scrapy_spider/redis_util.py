from typing import Dict

import redis

from config import ERROR_KEYS, CRAWLED_CATEGORY_KEYS, CRAWLED_ITEM_KEYS

# 创建 Redis 连接池

redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)


def write_error_to_redis(error_info: str, error_keys=ERROR_KEYS):
    # 获取 Redis 连接对象
    r = redis.Redis(connection_pool=redis_pool)
    # 将错误信息推入 Redis 列表
    r.lpush(error_keys, error_info)


def write_category_item_number_to_redis(category_url, item_count_info, category_keys=CRAWLED_CATEGORY_KEYS):
    # 获取 Redis 连接对象
    r = redis.Redis(connection_pool=redis_pool)
    # 将错误信息推入 Redis 列表
    r.hset(category_keys, category_url, item_count_info)  # 不够的要补1李爱
    print("log ", category_keys, category_url, item_count_info)


def write_item_to_redis(item_url, item_name, table_name=CRAWLED_ITEM_KEYS):
    # 获取 Redis 连接对象
    r = redis.Redis(connection_pool=redis_pool)
    # 将错误信息推入 Redis 列表
    r.hset(table_name, item_url, item_name)  # 不够的要补1李爱
    # print("log ", table_name, item_url, item_name)


def get_redis_hash(category_keys=CRAWLED_CATEGORY_KEYS) -> Dict:
    r = redis.Redis(connection_pool=redis_pool)
    result = r.hgetall(category_keys)
    return result


def hexists(field_key, category_keys):
    r = redis.Redis(connection_pool=redis_pool)
    if r.hexists(category_keys, field_key):
        return True
    else:
        return False


def init_root_url(spider_name, url):
    r = redis.Redis(connection_pool=redis_pool)
    r.lpush(f'{spider_name}:start_urls', url)
    print(f'{spider_name}:start_urls', url, "插入启动种子，开始抓取...")

def real_items_urls(spider_name):
    # 创建 Redis 连接
    r = redis.Redis(connection_pool=redis_pool)
    # 获取 list 的所有数据
    list_data = r.lrange(f'{spider_name}:items', 0, -1)
    # 输出字符串类型的列表
    str_list = [item.decode() for item in list_data]
    print(str_list)
    return str_list


def read_batch_redis_data(spider_name):
    r = redis.Redis(connection_pool=redis_pool)

    # 一次读取的元素数量
    batch_size = 3000

    redis_list_key = f'{spider_name}:items'
    # 获取 List 长度
    list_len = r.llen(redis_list_key)

    # 按批次读取元素
    for i in range(0, list_len, batch_size):
        # 计算本批次需要读取的元素范围
        start = i
        end = min(i + batch_size - 1, list_len - 1)

        # 读取本批次的元素值
        batch = r.lrange(redis_list_key, start, end)

        # 处理本批次读取的元素值
        for value in batch:
            # 提取item信息，然后写入
            pass
    # ...


if __name__ == '__main__':
    # init_root_url("amazon", "https://www.amazon.com/Best-Sellers/zgbs/")
    # result = real_items_urls()
    # print(result[1])
    # print(len(result))
    # print(1)
    r = redis.Redis(connection_pool=redis_pool)

    r.rpush('mylist', 'hello')
