import os

PROXY_USER = os.environ.get("PROXY_USER")
PROXY_PASSWORD = os.environ.get("PROXY_PASSWORD")
PROXY_HOST = os.environ.get("PROXY_HOST")
PROXY_PORT = os.environ.get("PROXY_PORT")
PROJECT_ROOT = os.path.dirname(__file__)

# debug 用
HEADLESS_MODE = bool(int(os.environ.get("HEADLESS_MODE", "0")))
IMAGE_MODE = bool(int(os.environ.get("HEADLESS_MODE", "0")))

# 可选，记录错误/ 新版本没用这几个变量
ERROR_KEYS = os.environ.get("ERROR_KEYS", "scrapy_error_urls")
CRAWLED_CATEGORY_KEYS = os.environ.get("CRAWLED_CATEGORY_KEYS", "crawled_category_info")
CRAWLED_ITEM_KEYS = os.environ.get("CRAWLED_ITEM_KEYS", "crawled_item_info")

print("-------config 配置:-------")
local_vars = {}
local_vars.update(locals())
config_vars = [[i, local_vars[i]] for i in local_vars if i[0].istitle()]
for i, v in config_vars:
    print(i, v)
print("-------------------------")
