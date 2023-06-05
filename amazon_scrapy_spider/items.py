# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass
from enum import Enum

import scrapy


class Level(Enum):
    RootLevel = 0  # 首页为0级 url = "https://www.amazon.com/Best-Sellers/zgbs/"
    FirstLevel = 1  # 定义第一次点击侧边的分类为树的1级别，从1级开始才会提取详细的 前100 的item
    SecondLevel = 2
    ThirdLevel = 3
    NotExistLevel = -1  # 就是此item 属于（这种爬法会有重复，不过，这样才嫩尽可能的保存一级类别开始的曾经关系）

    def __str__(self):
        return self.value


# middleware 的request 类型判断
class RequestType(Enum):
    Root = 0
    CategoryRequest = 1
    ItemRequest = 2


@dataclass
class Category:
    name: str  # 这个 root/first/second/third 这样存
    level: Level  # 这个类所在层级

    def __str__(self):
        return f"{self.name}:{self.level.value}"


# items
class CategoryPage(scrapy.Item):
    url = scrapy.Field()
    level = scrapy.Field()
    name = scrapy.Field()  # 从 Category中提取
    page_number = scrapy.Field()  # 只有两页，前100 item


# @dataclass
class Item(scrapy.Item):
    bsr = scrapy.Field()  # 就是对应主题下的排名
    title = scrapy.Field()  # title: str
    url = scrapy.Field()  # url: str
    belongs_category = scrapy.Field()  # belongs_category: Category  # 所在类别
    belongs_level = scrapy.Field()

    def __str__(self):
        return f"{self['bsr']}:{self['title']}:{self['belongs_category']}"


if __name__ == '__main__':
    print(Category("helloo", Level.FirstLevel))
