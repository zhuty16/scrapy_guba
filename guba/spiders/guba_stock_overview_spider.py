# -*- coding:utf-8 -*-

"""guba_stock_overview_spider"""

import re
import json
from scrapy import log
from scrapy.http import Request
from scrapy.conf import settings
from scrapy.spider import BaseSpider
from BeautifulSoup import BeautifulSoup
from guba.items import GubaStocksItem

HOST_URL = "http://guba.eastmoney.com/"
OVERVIEW_URL = "http://guba.eastmoney.com/remenba.aspx?type=1"


class GubaStockOverviewSpider(BaseSpider):
    """usage: scrapy crawl guba_stock_overview_spider --loglevel=INFO
    """
    name = 'guba_stock_overview_spider'

    def start_requests(self):
        request = Request(OVERVIEW_URL)
        yield request

    def parse(self, response):
        results = []
    	resp = response.body
    	soup = BeautifulSoup(resp)
        
        board_list = []
        ngbggul_ul = soup.find('ul', {'class': 'ngbggul'})

        if ngbggul_ul:
            for li in ngbggul_ul.findAll('li'):
                board_list.append(li.string)
        
        ngbggulbody_div = soup.find('div', {'class':'ngbggulbody'})
        if ngbggulbody_div:
            for idx, ngbglist_div in enumerate(ngbggulbody_div.findAll('div', {'class': 'ngbglistdiv'})):
                stock_type = board_list[idx]
                for a in ngbglist_div.findAll('a'):
                    stock_url = a.get('href')
                    if 'http://' not in stock_url:
                        stock_url = HOST_URL + stock_url
                    stock_id = re.search(r'\,(.*?)\.', stock_url).group(1)
                    
                    stock_name_list = a.string.split(')')

                    if len(stock_name_list) == 2:
                        stock_name = stock_name_list[1]
                    else:
                        stock_name = stock_name_list[0]

                    stock_dict = {'stock_url': stock_url, 'stock_type': stock_type, \
                    'stock_id': stock_id, 'stock_name': stock_name}
                    
                    item = GubaStocksItem()
                    for key in GubaStocksItem.RESP_ITER_KEYS:
                        item[key] = stock_dict[key]
                    
                    results.append(item)

        return results
