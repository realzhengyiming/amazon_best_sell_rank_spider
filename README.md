# amazon scrapy spider  
目前亚马逊bsr多级爬虫的方案，selenium + scrapy_redis + proxy ip 解决反爬的问题。  

# required  
## worker node (python env)  
conda create -n amazon_spider python=3.10  
conda activate amazon_spider  
pip install -r requirements.txt  

## master node  
安装好redis，且内存容量需要足够，worker 爬虫的item，request，dupefilter会存储在上面  
默认爬虫连接localhost 6379 无密码的本地redis，如有需要修改，则到  
amazon_scrapy_spider/spider/amazon_spider.py内的custom_settings内修改。  


# launch
1. 配置好spider 内的redis地址  
test_scrapy_spider/amazon_scrapy_spider/spiders/amazon_spider.py  

2. 给redis写入分布式爬虫启动的种子目录（第一次启动的时候）
lpush amazon:start_urls https://www.amazon.com/Best-Sellers/zgbs/  


3. 配置好worker环境，启动worker爬虫  
// 不配置这个的话，默认就不使用代理
export PROXY_HOST=your_proxy_host  
export PROTY_PORT=your_proxy_port  
export PROXY_USERNAME=your_username  
export PROXY_PASSWORD=your_password  
   
cd test_scrapy_spider  
scrapy crawl amazon  

# note  
目前，您的分布式爬虫方案中，每次从 Redis 中取出种子 URL 开始进行抓取任务。当需要停止某个 worker 时，可以通过在命令行中使用 CTRL+C 捕获 SIGINT 信号来优雅地终止 spider 进程。这样，爬虫会消耗完当前的请求，自动保存进度，并等待状态优雅地保存结束后再退出。如果在此过程中强制关闭（例如快速两次 CTRL+C 或者其他方式杀死进程），就会导致尚未完成的请求丢失，进而造成数据遗漏。

对于多级分类（多叉树结构）的情况，如果遗漏了 root 请求、某个分支的父节点或者一些后续子节点，可能会导致整棵树的部分数据无法获取。考虑到这一点，建议在终止爬虫，特别是在一个 worker 要停止工作时，务必ctrl + c 一次，然后等候爬虫把 URL 和相应的状态存储到 Redis 中，以防数据丢失。这样即使有 worker 异常终止，也能够保留已经完成的任务进度，方便下一次重启后继续进行数据采集。

# 还未做的事情  
详情页解析还没做，不过难度响度小一些，只需要完善解析的部分就可以了  