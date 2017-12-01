# coding=utf-8

import sys
import config
import utils
import datetime

from scrapy.spiders import Spider
from scrapy.http import Request, FormRequest
from sql import SqlManager


# class FreeIPProxy(object):
#     ip = CharField(unique=True)
#     port = IntegerField()
#     country = TextField()
#     anonymity = IntegerField()
#     https = CharField()
#     speed = FloatField()
#     source = CharField()
#     save_time = TimestampField()
#     vali_count = IntegerField()


class BaseSpider(Spider):
    name = 'basespider'

    def __init__(self, *a, **kw):
        super(BaseSpider, self).__init__(*a, **kw)

        self.urls = []
        self.headers = {}
        self.timeout = 10
        self.is_record_web_page = False
        self.proxy = None
        self.method = 'GET'
        self.formdata = {}

        self.sql = SqlManager()

    def init(self):
        self.meta = {
            'download_timeout': self.timeout,
        }
        if self.proxy:
            self.meta['proxy'] = self.proxy

        self.dir_log = 'log/proxy/%s' % self.name
        utils.make_dir(self.dir_log)
        self.sql.init_proxy_table(config.free_ipproxy_table)

    def start_requests(self):
        for i, url in enumerate(self.urls):
            if self.method == 'POST':
                yield FormRequest(
                    url=url,
                    # headers=self.headers,
                    formdata=self.formdata,
                    meta=self.meta,
                    dont_filter=True,
                    callback=self.parse_page,
                    errback=self.error_parse,
                )
            else:
                yield Request(
                    url=url,
                    # headers=self.headers,
                    method=self.method,
                    meta=self.meta,
                    dont_filter=True,
                    callback=self.parse_page,
                    errback=self.error_parse,
                )

    def parse_page(self, response):
        self.write(response.body)
        pass

    def error_parse(self, failure):
        request = failure.request
        pass

    def add_proxy(self, proxy):
        # query = {
        #     'ip': proxy.ip,
        # }
        # update_set = {
        #     '$set': proxy.get_dict()
        # }
        # self.freeproxy.find_one_and_update(query, update_set, upsert=True)
        self.sql.insert_proxy(config.free_ipproxy_table, proxy)

    def write(self, data):
        if self.is_record_web_page:
            with open('%s/%s.html' % (self.dir_log, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')),
                      'w') as f:
                f.write(data)
                f.close()

    # def close(spider, reason):
    #     spider.sql.commit()
