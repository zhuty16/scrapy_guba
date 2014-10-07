# -*- coding: utf-8 -*-

# Scrapy settings for guba project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import os

BOT_NAME = 'guba'

SPIDER_MODULES = ['guba.spiders']
NEWSPIDER_MODULE = 'guba.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'guba (+http://www.yourdomain.com)'

# The amount of time (in secs) that the downloader should wait 
# before downloading consecutive pages from the same spider
DOWNLOAD_DELAY = 0.5 # 50 ms of delay

# If enabled, Scrapy will wait a random amount of time 
# (between 0.5 and 1.5 * DOWNLOAD_DELAY) while fetching requests 
# from the same spider.
# This randomization decreases the chance of the crawler 
# being detected (and subsequently blocked) by sites which analyze 
# requests looking for statistically significant similarities in 
# the time between their requests.
# RANDOMIZE_DOWNLOAD_DELAY = True

# 期望减少mongodb的压力
# Maximum number of concurrent items (per response) to process in parallel in ItemPipeline, Default 100
CONCURRENT_ITEMS = 100
# The maximum number of concurrent (ie. simultaneous) requests that will be performed by the Scrapy downloader, Default 16.
CONCURRENT_REQUESTS = 2
# The maximum number of concurrent (ie. simultaneous) requests that will be performed to any single domain, Default: 8.
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# 不需要默认的180秒,更多的机会留给重试
# The amount of time (in secs) that the downloader will wait before timing out, Default: 180.
DOWNLOAD_TIMEOUT = 15

AUTOTHROTTLE_ENABLED = True # Enables the AutoThrottle extension.
AUTOTHROTTLE_START_DELAY = 2.0 # The initial download delay (in seconds).Default: 5.0
AUTOTHROTTLE_MAX_DELAY = 60.0 # The maximum download delay (in seconds) to be set in case of high latencies.
AUTOTHROTTLE_CONCURRENCY_CHECK_PERIOD = 100 # How many responses should pass to perform concurrency adjustments.
AUTOTHROTTLE_DEBUG = True

RETRY_HTTP_CODES = [500, 502, 503, 504, 408]

SPIDER_MIDDLEWARES = {
    'scrapy.contrib.spidermiddleware.offsite.OffsiteMiddleware': None,
    'scrapy.contrib.spidermiddleware.referer.RefererMiddleware': None,
    'scrapy.contrib.spidermiddleware.urllength.UrlLengthMiddleware': None,
    'scrapy.contrib.spidermiddleware.depth.DepthMiddleware': None,
    #'utils4scrapy.middlewares.RetryErrorResponseMiddleware': 940,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.robotstxt.RobotsTxtMiddleware': None,
    'scrapy.contrib.downloadermiddleware.httpauth.HttpAuthMiddleware': None,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'scrapy.contrib.downloadermiddleware.defaultheaders.DefaultHeadersMiddleware': None,
    'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware': None,
    'scrapy.contrib.downloadermiddleware.cookies.CookiesMiddleware': None,
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': None,
    'scrapy.contrib.downloadermiddleware.httpcache.HttpCacheMiddleware': None
}

ITEM_PIPELINES = [
    'guba.pipelines.MongodbPipeline'
]

EXTENSIONS = {
    'scrapy.webservice.WebService': None,
    'scrapy.telnet.TelnetConsole': None
}


RETRY_TIMES = 3 - 1
MONGOD_HOST = '219.224.135.60'
MONGOD_PORT = 27017
MONGOD_DB = 'guba'
GUBA_POST_COLLECTION = 'post'
GUBA_STOCK_COLLECTION = 'stock'
