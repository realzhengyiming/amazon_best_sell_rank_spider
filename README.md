# amazon scrapy spider  
目前亚马逊bsr多级爬虫的方案，selenium + scrapy_redis + proxy ip 解决反爬的问题。

# required
## worker node (python env)
conda create -n amazon_spider python=3.10
conda activate amazon_spider
pip install -r requirements.txt

## master node  
安装好redis，且内存容量需要足够，worker 爬虫的item，request，dupefilter会存储在上面


# launch
python launch.py

or bash
scrapy crawl amazon