# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import time
import json
from scrapy import log
from twisted.internet.threads import deferToThread
from guba.items import GubaPostItem, GubaStocksItem
from guba.utils import _default_mongo


class MongodbPipeline(object):
    def __init__(self, db, host, port, post_collection, stock_collection):
        self.db_name = db
        self.host = host
        self.port = port
        self.db = _default_mongo(host, port, usedb=db)
        self.post_collection = post_collection
        self.stock_collection = stock_collection
        log.msg('Mongod connect to {host}:{port}:{db}'.format(host=host, port=port, db=db), level=log.INFO)

    @classmethod
    def from_settings(cls, settings):
        db = settings.get('MONGOD_DB', None)
        host = settings.get('MONGOD_HOST', None)
        port = settings.get('MONGOD_PORT', None)
        post_collection = settings.get('GUBA_POST_COLLECTION', None)
        stock_collection = settings.get('GUBA_STOCK_COLLECTION', None)

        return cls(db, host, port, post_collection, stock_collection)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        if isinstance(item, GubaPostItem):
            return deferToThread(self.process_post, item, spider)
        elif isinstance(item, GubaStocksItem):
            return deferToThread(self.process_stock, item, spider)

    def process_item_sync(self, item, spider):
        if isinstance(item, GubaPostItem):
            return self.process_post(item, spider)
        elif isinstance(item, GubaStocksItem):
            return self.process_stock(item, spider)

    def update_post(self, post_collection, post):
        updates = {}
        updates['last_modify'] = time.time()
        for key in GubaPostItem.PIPED_UPDATE_KEYS:
            if post.get(key) is not None:
                updates[key] = post[key]

        updates_modifier = {'$set': updates}
        self.db[post_collection].update({'_id': post['_id']}, updates_modifier)

    def process_post(self, item, spider):
        post = item.to_dict()
        post['_id'] = post['post_id']
        
        if self.db[self.post_collection].find({'_id': post['_id']}).count():
            self.update_post(self.post_collection, post)
        else:
            try:
                post['first_in'] = time.time()
                post['last_modify'] = post['first_in']
                self.db[self.post_collection].insert(post)
            except pymongo.errors.DuplicateKeyError:
                self.update_post(self.post_collection, post)

        return item

    def update_stock(self, stock_collection, stock):
        updates = {}
        updates['last_modify'] = time.time()
        for key in GubaStocksItem.PIPED_UPDATE_KEYS:
            if stock.get(key) is not None:
                updates[key] = stock[key]

        updates_modifier = {'$set': updates}
        self.db[stock_collection].update({'_id': stock['_id']}, updates_modifier)

    def process_stock(self, item, spider):
        stock = item.to_dict()
        stock['_id'] = stock['stock_id']

        if self.db[self.stock_collection].find({'_id': stock['_id']}).count():
            self.update_stock(self.stock_collection, stock)
        else:
            try:
                stock['first_in'] = time.time()
                stock['last_modify'] = stock['first_in']
                self.db[self.stock_collection].insert(stock)
            except pymongo.errors.DuplicateKeyError:
                self.update_stock(self.stock_collection, stock)

        return item
