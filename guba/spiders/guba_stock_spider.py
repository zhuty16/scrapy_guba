# -*- coding:utf-8 -*-

"""guba_stock_spider"""

import re
import json
from scrapy.http import Request
from scrapy.conf import settings
from scrapy.spider import BaseSpider
from BeautifulSoup import BeautifulSoup
from guba.items import GubaPostItem
from guba.utils import _default_mongo


LIST_URL = "http://guba.eastmoney.com/list,{stock_id},f_{page}.html"
POST_URL = "http://guba.eastmoney.com/news,{stock_id},{post_id}.html"


class GubaStockSpider(BaseSpider):
    """usage: scrapy crawl guba_stock_spider -a since_idx=1 -a max_idx=100 --loglevel=INFO
    """
    name = 'guba_stock_spider'

    def __init__(self, since_idx, max_idx):
        self.since_idx = int(since_idx)
        self.max_idx = int(max_idx)

    def start_requests(self):
        stock_ids = self.prepare()
        for stock_id in stock_ids:
            request = Request(LIST_URL.format(stock_id=stock_id, page=1))
            request.meta['stock_id'] = stock_id
            request.meta['page'] = 1

            yield request

    def parse(self, response):
    	page = response.meta['page']
    	resp = response.body

    	soup = BeautifulSoup(resp)
        stock_title = soup.html.head.title
        stock_id = re.search(r'股吧_(.*?)股吧', str(stock_title)).group(1).decode('utf8')
        stock_name = re.search(r'_(.*?)股吧', str(stock_title)).group(1).decode('utf8')

        for item_soup in soup.findAll('div', {'class':'articleh'}):
            item_soup = str(item_soup)
            clicks = re.search(r'"l1">(.*?)<', item_soup).group(1)

            replies = re.search(r'"l2">(.*?)<', item_soup).group(1)

            stockholder = re.search(r'dong">(.*?)<', item_soup)
            if stockholder:
                stockholder = stockholder.group(1).decode('utf8')
            else:
                stockholder = ''
        
            post_title = re.search(r'title="(.*?)"', item_soup).group(1).decode('utf8')
            
            lastReplyTime = re.search(r'"l5">(.*?)<', item_soup).group(1)
            
            post_id = re.search(r'news,.*?,(.*?).html', item_soup).group(1)
            
            item_dict = {'title': post_title, 'stock_id': stock_id, 'stock_name': stock_name, \
            'clicks': clicks, 'replies': replies, 'stockholder': stockholder, \
            'lastReplyTime': lastReplyTime, 'post_id': post_id}

            item = GubaPostItem()
            for key in GubaPostItem.LIST_PAGE_KEYS:
                item[key] = item_dict[key]

            request = Request(POST_URL.format(stock_id=response.meta['stock_id'], post_id=post_id), callback=self.parsePost)
            request.meta['item'] = item

            yield request
        
        page += 1
        request = Request(LIST_URL.format(stock_id=response.meta['stock_id'], page=page))
        request.meta['stock_id'] = response.meta['stock_id']
        request.meta['page'] = page

        yield request
      
    def parsePost(self, response):
    	item = response.meta['item']
    	resp = response.body
        postsoup = BeautifulSoup(resp)
        
        content = postsoup.find('div',{'class':'stockcodec'}).text.encode('utf8').decode('utf8')     
        
        user_name = postsoup.findAll('div', {'id': 'zwconttbn'})[0].text.encode('utf8').replace('：', '').decode('utf8')
        
        zwconbotl = str(postsoup.findAll('div', {'id': 'zwconbotl'})[0])
        releaseTime = re.search(r'：(.*?)<', zwconbotl).group(1)

        item_dict = {'content': content, 'user_name': user_name, 'releaseTime': releaseTime}

        for key in GubaPostItem.POST_PAGE_KEYS:
        	item[key] = item_dict[key]

        return item

    def prepare(self):
        db = settings.get('MONGOD_DB', None)
        host = settings.get('MONGOD_HOST', None)
        port = settings.get('MONGOD_PORT', None)
        stock_collection = settings.get('GUBA_STOCK_COLLECTION', None)
        
        stock_ids = []
        db = _default_mongo(host, port, usedb=db)
        cursor = db[stock_collection].find().limit(100)
        for stock in cursor:
            stock_ids.append(stock['stock_id'])
        
        return stock_ids
