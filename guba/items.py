# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class GubaPostItem(Item):
    post_id = Field() # 帖子唯一标识
    stock_name = Field() # 股票名称
    stock_id = Field() # 股票代码
    title = Field() # 标题
    content = Field() # 内容
    clicks = Field() # 点击数
    replies = Field() # 回复数
    releaseTime = Field() # 发表时间
    lastReplyTime = Field() # 最后回复时间
    user_name = Field() # 作者
    stockholder = Field() # 是否是股东    

    LIST_PAGE_KEYS = ['stock_id', 'stock_name', 'clicks', 'replies', \
    'stockholder', 'title', 'lastReplyTime', 'post_id']

    POST_PAGE_KEYS = ['content', 'user_name', 'releaseTime']

    PIPED_UPDATE_KEYS = ['stock_id', 'stock_name', 'clicks', 'replies', \
    'stockholder', 'title', 'lastReplyTime', \
    'content', 'user_name', 'releaseTime']

    def __init__(self):
        super(GubaPostItem, self).__init__()

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v, (GubaPostItem, GubaStocksItem)):
                d[k] = v.to_dict()
            else:
                d[k] = v
        return d


class GubaStocksItem(Item):
    stock_id = Field()
    stock_name = Field()
    stock_type = Field()
    stock_url = Field()

    RESP_ITER_KEYS = ['stock_id', 'stock_name', 'stock_type', 'stock_url']
    
    PIPED_UPDATE_KEYS = ['stock_name', 'stock_type', 'stock_url']

    def __init__(self):
        super(GubaStocksItem, self).__init__()

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v, (GubaPostItem, GubaStocksItem)):
                d[k] = v.to_dict()
            else:
                d[k] = v
        return d
