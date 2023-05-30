import os

PROXY_USER = os.environ.get("PROXY_USER")
PROXY_PASSWORD = os.environ.get("PROXY_PASSWORD")
PROXY_HOST = os.environ.get("PROXY_HOST")
PROXY_PORT = os.environ.get("PROXY_PORT")
PROJECT_ROOT = os.path.dirname(__file__)

# debug 用
HEADLESS_MODE = bool(os.environ.get("HEADLESS_MODE", False))
IMAGE_MODE = bool(os.environ.get("HEADLESS_MODE", False))

# 可选，记录错误
ERROR_KEYS = os.environ.get("ERROR_KEYS", "scrapy_error_urls")
CRAWLED_CATEGORY_KEYS = os.environ.get("CRAWLED_KEYS", "crawled_category_info")
ITEM_URLS = "ITEM_URL"

print("-------config 配置:-------")
local_vars = {}
local_vars.update(locals())
config_vars = [[i, local_vars[i]] for i in local_vars if i[0].istitle()]
for i, v in config_vars:
    print(i, v)
print("-------------------------")
