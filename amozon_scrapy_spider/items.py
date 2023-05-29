# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass
from enum import Enum

import scrapy


class TreeLevel(Enum):
    ZeroLevel = 0  # 首页为0级 url = "https://www.amazon.com/Best-Sellers/zgbs/"
    FirstLevel = 1  # 定义第一次点击侧边的分类为树的1级别，从1级开始才会提取详细的 前100 的item
    SecondLevel = 2
    ThirdLevel = 3
    NotExistLevel = -1  # 就是此item 属于（这种爬法会有重复，不过，这样才嫩尽可能的保存一级类别开始的曾经关系）


@dataclass
class Category:
    name: str  # 这个类的名字
    tree_level: TreeLevel  # 这个类所在层级


# @dataclass
class Item(scrapy.Item):
    bsr = scrapy.Field()  # 就是对应主题下的排名
    title = scrapy.Field()  # title: str
    url = scrapy.Field()  # url: str
    belongs_category = scrapy.Field()  # belongs_category: Category  # 所在类别
    first_level = scrapy.Field()  # first_level: Category  # 第一级 (一定有）
    second_level = scrapy.Field()  # second_level: Category = None  # 第二级（可以没有）
    third_level = scrapy.Field()  # third_level: Category = None  # 第三级（可以没有）

# class AmazonScrapySpiderItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass
