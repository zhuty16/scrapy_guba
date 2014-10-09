# -*- coding:utf-8 -*-
    
"""guba_stock_spider"""

import re
import json
from scrapy import log
from scrapy.http import Request
from scrapy.conf import settings
from scrapy.spider import BaseSpider
from BeautifulSoup import BeautifulSoup
from guba.items import GubaPostItem
from guba.utils import _default_mongo, datetimestr2ts, postdate2ts

LIST_URL = "http://guba.eastmoney.com/list,{stock_id},f_{page}.html"
POST_URL = "http://guba.eastmoney.com/news,{stock_id},{post_id}.html"

class GubaStockSpider(BaseSpider):
    """usage: scrapy crawl guba_stock_spider -a stock_type_idx=1 -a end_date=2014-10-08 --loglevel=INFO
       遇到end_date的0时时刻即停止
    """
    name = 'guba_stock_spider'

    def __init__(self, stock_type_idx, end_date):
        self.stock_type_list = ['沪A', '沪B', '深A', '深B']
        self.stock_type_idx = int(stock_type_idx)
        self.end_ts = datetimestr2ts(end_date)

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
        
        stoped = False
        for item_soup in soup.findAll('div', {'class':'articleh'}):
            item_soup = str(item_soup)
            
            clicks = re.search(r'"l1">(.*?)<', item_soup).group(1)

            replies = re.search(r'"l2">(.*?)<', item_soup).group(1)

            stockholder = re.search(r'dong">(.*?)<', item_soup)
            if stockholder:
                stockholder = stockholder.group(1).decode('utf8')
            else:
                stockholder = ''
            
            post_title = re.search(r'>(.*?)</a>', item_soup).group(1).decode('utf8')
           
            post_date = re.search(r'"l6">(.*?)<', item_soup).group(1)
            
            post_ts = postdate2ts(post_date)
            if post_ts < self.end_ts:
                stoped = True
                log.msg('[stock]: {stock_id} stopped'.format(stock_id=stock_id))
                break

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

        if not stoped:
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
        stock_type = self.stock_type_list[self.stock_type_idx]

        stock_ids = []
        db = _default_mongo(host, port, usedb=db)
        cursor = db[stock_collection].find({'stock_type': stock_type})
        for stock in cursor:
            stock_ids.append(stock['stock_id'])

        log.msg(str(len(stock_ids)))
        return stock_ids
