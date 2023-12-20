# Amazon Scrapy Spider

Currently, the solution for the multi-level Amazon BSR (Best Sellers Rank) spider involves using Selenium, Scrapy Redis, and proxy IPs to address anti-scraping measures.

## Project Spiders
This project consists of four spiders, organized into two groups:
+ BSR category spider
+ BSR item detail spider
+ New release category spider
+ New release item detail spider

Spiders within a group have interdependencies; the item detail spider's URL seeds depend on the preceding category spider. The two groups operate independently, and data storage in Redis is segmented into different tables.

# Required
## Worker Node (Python Environment)
```bash
conda create -n amazon_spider python=3.10
conda activate amazon_spider
pip install -r requirements.txt
```

## Master Node
Install Redis with sufficient memory capacity. The item, request, and dupefilter data of the worker spiders will be stored in the Redis database. The default spider connects to localhost:6379 with no password. Modify if needed in `amazon_scrapy_spider/spider/amazon_spider.py`. (This code was tested using a locally hosted Redis service through Docker.)

# Launch
## Launching BSR Category and Item Detail Spiders
1. Configure the Redis address in the spider:
   `test_scrapy_spider/amazon_scrapy_spider/spiders/amazon_spider.py`

2. Write the seed directory for the distributed spider startup into Redis (first-time startup). This seed is hardcoded and corresponds to the one in the middleware. Include the trailing slash.
   ```bash
   lpush amazon:start_urls https://www.amazon.com/Best-Sellers/zgbs/
   ```

3. Configure the worker environment and start the worker spider:
   ```bash
   export PROXY_HOST=your_proxy_host
   export PROTY_PORT=your_proxy_port
   export PROXY_USERNAME=your_username
   export PROXY_PASSWORD=your_password

   cd test_scrapy_spider
   scrapy crawl amazon
   ```

4. The item detail spider is independent and follows the same distributed structure. Start it by:
   ```bash
   cd test_scrapy_spider
   scrapy crawl amazon_item_detail
   ```

## Launching New Release Category and Item Detail Spiders
1. Configure the Redis address in the spider:
   `test_scrapy_spider/amazon_scrapy_spider/spiders/amazon_spider_new_release.py`

2. Write the seed directory for the distributed spider startup into Redis (first-time startup). This seed is hardcoded and corresponds to the one in the middleware. It is recommended to directly copy from the readme.
   ```bash
   lpush amazon_new_relase:start_urls https://www.amazon.com/gp/new-releases/ref=zg_bs_tab
   ```

3. Configure the worker environment and start the worker spider:
   ```bash
   export PROXY_HOST=your_proxy_host
   export PROTY_PORT=your_proxy_port
   export PROXY_USERNAME=your_username
   export PROXY_PASSWORD=your_password

   cd test_scrapy_spider
   scrapy crawl amazon_new_relase
   ```

4. The item detail spider is independent and follows the same distributed structure. Start it by:
   ```bash
   cd test_scrapy_spider
   scrapy crawl amazon_new_release_item_detail
   ```

# Special Launch Scenarios
If you encounter lost requests due to forceful interruption, modify and construct the `tool/add_request_to_queue.py` main. Follow the example in main to construct requests, write them to the Redis queue, and restart the spider.

# Notes
In your distributed spider solution, each task starts fetching URLs from Redis. When stopping a worker, gracefully terminate the spider process by capturing the SIGINT signal with CTRL+C in the command line. This allows the spider to consume the current requests, automatically save progress, and wait for a graceful exit after completing the ongoing tasks. Forcibly closing (e.g., quick CTRL+C twice or other abrupt process termination) can lead to incomplete requests and data loss.

For multi-level categorization (tree structure), missing root requests, parent nodes of a branch, or some subsequent child nodes may result in incomplete data for the entire tree. When stopping a spider, especially when a worker is about to stop, it is recommended to use CTRL+C once, allowing the spider to store URLs and corresponding states in Redis before waiting for a graceful exit to prevent data loss. Even if a worker terminates abnormally, the completed task progress can be retained, facilitating data collection in subsequent restarts.

# Pending Tasks
Optimize the current proxy IP request prevention solution to reduce operational costs and switch to more cost-effective packages.