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
1. 配置好spider 内的redis地址
test_scrapy_spider/amazon_scrapy_spider/spiders/amazon_spider.py

2. 给redis写入分布式爬虫启动的种子目录（第一次启动的时候）
lpush amazon:start_urls https://www.amazon.com/Best-Sellers/zgbs/

3. 配置好worker环境，启动worker爬虫
cd test_scrapy_spider
scrapy crawl amazon
   
# note  
目前请求是从redis每次pop取出种子url开始爬取。
命令行启动爬虫后如果希望停止此worker，
CTRL+C 一次就可以，爬虫会消耗完目前的请求，然后自动保存目前的进度， 等他优雅的保存完状态就可以了。
如果ctrl + c两次强制关闭，或者是通过其他方式强制杀掉进程，那就会丢失还没爬取完的请求。造成数据遗漏。
特别是对于多级分类（多叉树结构）如果遗漏掉了root的请求，后面全部都停止爬取，或者某个分支的父节点，往后几个等级的子节点就也会没法爬取




python launch.py

or bash
scrapy crawl amazon